#!/bin/bash

apt install unzip

trap "" SIGTERM
killall -r node-side-mon
trap - SIGTERM

if [ ! -f grok_exporter-1.0.0.RC5.linux-amd64.zip ]
then
    wget https://github.com/fstab/grok_exporter/releases/download/v1.0.0.RC5/grok_exporter-1.0.0.RC5.linux-amd64.zip
fi
unzip grok_exporter-*

#cp process-exporter.yml.in process-exporter.yml
cat > process-exporter.yml <<****
process_names:
  - exe:
    - skaled
    cmdline:
    - --config /skale_schain_data/schain_(?P<schainName>.+).json
    name: "{{.Matches.schainName}}"
  - exe:
    - skaled
    cmdline:
    - --ws-port (?P<wsPort>\d+)
    name: "{{.ExeBase}}:{{.Matches.wsPort}}"
  - exe:
    - telegraf
    cmdline:
    - --watch-config notify
****

docker run --rm -p 9256:9256 --privileged -v /proc:/host/proc -v `pwd`:/config --name pexporter ncabatoff/process-exporter --procfs /host/proc -config.path /config/process-exporter.yml&

make_grok_input () {
  local IMAGES=($(docker ps --no-trunc --format '{{.ID}} {{.Image}}'    | grep 'schain' | cut -d ' ' -f 1))
  local  NAMES=($(docker ps --no-trunc --format '{{.Image}} {{.Names}}' | grep 'schain' | cut -d ' ' -f 2-))

  # create symlinks
  mkdir log_links 2>/dev/null
  cd log_links
  for I in ${!IMAGES[@]}
  do
    rm -f ${NAMES[$I]}
    ln -s /var/lib/docker/containers/${IMAGES[$I]} ${NAMES[$I]} 2>/dev/null
  done
  cd ..

  local INPUT="  type: file
  readall: true
  fail_on_missing_logfile: false
  paths:"
  for I in ${NAMES[@]}
  do
    INPUT="${INPUT}"$'\n'"  - $(realpath -s ./log_links/$I/*.log)"
  done
  echo "$INPUT"
}


create_grok_yml () {
INPUT="$INPUT" PORT=9144 PATTERNS="$PATTERNS" envsubst >grok-exporter.yml <<********************************************
global:
  config_version: 3
imports:
- type: grok_patterns
  dir: ${PATTERNS}
grok_patterns:
  - 'C_PREFIX \[%{TIMESTAMP_ISO8601}\] \[%{NUMBER:node_id}:%{WORD}\] \[%{WORD}\]'
  - 'C_PREFIX_BLOCK %{C_PREFIX} %{NUMBER}'
  - 'TIME_PREFIX %{TIMESTAMP_ISO8601}\s+'
input:
${INPUT}
metrics:
- type: gauge
  name: logs_BLOCK_COMMITED
  help: Block committed in bin-consensus
  match: '%{C_PREFIX_BLOCK}:BLOCK_COMMITED: PRPSR:%{NUMBER:proposer}:BID: %{NUMBER:block_id}'
  value: '{{.block_id}}'
  labels:
    node_id: '{{.node_id}}'
    proposer: '{{.proposer}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: counter
  name: logs_PRPSR
  help: Total number of proposals sent by each proposer
  match: '%{C_PREFIX_BLOCK}:BLOCK_COMMITED: PRPSR:%{NUMBER:proposer}:BID: %{NUMBER:block_id}'
  value: 1
  labels:
    node_id: '{{.node_id}}'
    proposer: '{{.proposer}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_addBlockProposal
  help: Block proposal received
  match: '%{C_PREFIX_BLOCK}:addBlockProposal blockID_=%{NUMBER:blockID} proposerIndex=%{NUMBER:proposerIndex}'
  value: '{{.blockID}}'
  labels:
    proposerIndex: '{{.proposerIndex}}'
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: counter
  name: logs_daProof
  help: DA proof received for block number
  match: '%{C_PREFIX} %{NUMBER:current_block}:Adding daProof'
  value: '1'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_PROPOSING
  help: Bin-cons proposing block
  match: '%{C_PREFIX_BLOCK}:PROPOSING BLOCK NUMBER:%{NUMBER:block_id}'
  value: '{{.block_id}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_BLOCK_DECIDED
  help: 1 bin-cons ended OK
  match: '%{C_PREFIX_BLOCK}:BLOCK_DECIDED: PRPSR:%{NUMBER:proposer}:BID: %{NUMBER:block_id}'
  value: '{{.block_id}}'
  labels:
    proposer: '{{.proposer}}'
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_received
  help: Number of txns in received queue
  match: '%{TIME_PREFIX}m_received = %{NUMBER:received}'
  value: '{{.received}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_sent
  help: Number of txns sent to cons
  match: '%{TIME_PREFIX}sent_to_consensus = %{NUMBER:sent} got_from_consensus = %{NUMBER:got} m_transaction_cache = %{NUMBER:cache} m_tq = %{NUMBER:tq} m_bcast_counter = %{NUMBER:bcast_counter}'
  value: '{{.sent}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_got
  help: Number of txns got committed
  match: '%{TIME_PREFIX}sent_to_consensus = %{NUMBER:sent} got_from_consensus = %{NUMBER:got} m_transaction_cache = %{NUMBER:cache} m_tq = %{NUMBER:tq} m_bcast_counter = %{NUMBER:bcast_counter}'
  value: '{{.got}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_tq
  help: Number of txns in transaction queue
  match: '%{TIME_PREFIX}sent_to_consensus = %{NUMBER:sent} got_from_consensus = %{NUMBER:got} m_transaction_cache = %{NUMBER:cache} m_tq = %{NUMBER:tq} m_bcast_counter = %{NUMBER:bcast_counter}'
  value: '{{.tq}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_imported
  help: Number of txns in block
  match: '%{TIME_PREFIX}Successfully imported %{NUMBER} of %{NUMBER:num} transactions'
  value: '{{.num}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: counter
  name: logs_queued
  help: Transaction added to Transaction Queue
  match: '%{TIME_PREFIX}Queued vaguely legit-looking transaction'
  value: '1'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: counter
  name: logs_requests
  help: JSON-RPC Requests counter
  match: '%{TIME_PREFIX}%{URI} >>> %{GREEDYDATA}'
  value: '1'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: counter
  name: logs_PARTIAL
  help: PARTIAL catch-up
  match: '%{TIME_PREFIX}PARTIAL'
  value: '1'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_CWT
  help: Consensus Wait Time
  match: '%{C_PREFIX_BLOCK}:CWT:%{NUMBER:cwt_value}'
  value: '{{.cwt_value}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_TLWT
  help: Transaction Latency Wait Time
  match: '%{C_PREFIX_BLOCK}:CWT:%{NUMBER:cwt_value}:TLWT:%{NUMBER:tlwt}'
  value: '{{.tlwt}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_SBPT
  help: SBPT metric
  match: '%{C_PREFIX_BLOCK}:CWT:%{NUMBER:cwt_value}:TLWT:%{NUMBER:tlwt}:SBPT:%{NUMBER:sbpt}'
  value: '{{.sbpt}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_BITE
  help: BITE metric
  match: '%{C_PREFIX_BLOCK}:CWT:%{NUMBER:cwt_value}:TLWT:%{NUMBER:tlwt}:SBPT:%{NUMBER:sbpt}:BITE_DECRYPTED_TXS:%{NUMBER:bite_decrypted_txs}'
  value: '{{.bite_decrypted_txs}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_BCT
  help: Block Commit Time (ms)
  match: '%{C_PREFIX_BLOCK}:BCT:%{NUMBER:bct}:BFST:%{NUMBER}:PST:%{NUMBER}'
  value: '{{.bct}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_BFST
  help: Block Finalization Stage Time (ms)
  match: '%{C_PREFIX_BLOCK}:BCT:%{NUMBER}:BFST:%{NUMBER:bfst}:PST:%{NUMBER}'
  value: '{{.bfst}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_PST
  help: Proposal Stage Time (ms)
  match: '%{C_PREFIX_BLOCK}:BCT:%{NUMBER}:BFST:%{NUMBER}:PST:%{NUMBER:pst}'
  value: '{{.pst}}'
  labels:
    node_id: '{{.node_id}}'
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_SWT
  help: Sync Wait Time
  match: 'SWT:%{NUMBER:swt}:BFT:%{NUMBER}:TQBYTES:CTQ:%{NUMBER}:FTQ:%{NUMBER}:TQSIZE:CTQ:%{NUMBER}:FTQ:%{NUMBER}'
  value: '{{.swt}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_BFT
  help: Block Finalization Time
  match: 'SWT:%{NUMBER}:BFT:%{NUMBER:bft}:TQBYTES:CTQ:%{NUMBER}:FTQ:%{NUMBER}:TQSIZE:CTQ:%{NUMBER}:FTQ:%{NUMBER}'
  value: '{{.bft}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_TQBYTES_CTQ
  help: Transaction Queue Bytes - CTQ Value
  match: 'SWT:%{NUMBER}:BFT:%{NUMBER}:TQBYTES:CTQ:%{NUMBER:tqbytes_ctq}:FTQ:%{NUMBER}:TQSIZE:CTQ:%{NUMBER}:FTQ:%{NUMBER}'
  value: '{{.tqbytes_ctq}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_TQBYTES_FTQ
  help: Transaction Queue Bytes - FTQ Value
  match: 'SWT:%{NUMBER}:BFT:%{NUMBER}:TQBYTES:CTQ:%{NUMBER}:FTQ:%{NUMBER:tqbytes_ftq}:TQSIZE:CTQ:%{NUMBER}:FTQ:%{NUMBER}'
  value: '{{.tqbytes_ftq}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_TQSIZE_CTQ
  help: Transaction Queue Size - CTQ Value
  match: 'SWT:%{NUMBER}:BFT:%{NUMBER}:TQBYTES:CTQ:%{NUMBER}:FTQ:%{NUMBER}:TQSIZE:CTQ:%{NUMBER:tqsize_ctq}:FTQ:%{NUMBER}'
  value: '{{.tqsize_ctq}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
- type: gauge
  name: logs_TQSIZE_FTQ
  help: Transaction Queue Size - FTQ Value
  match: 'SWT:%{NUMBER}:BFT:%{NUMBER}:TQBYTES:CTQ:%{NUMBER}:FTQ:%{NUMBER}:TQSIZE:CTQ:%{NUMBER}:FTQ:%{NUMBER:tqsize_ftq}'
  value: '{{.tqsize_ftq}}'
  labels:
    logfile: '{{gsub .logfile ".*/log_links/(.+)/.*-json.log" "\\\\1"}}'
server:
  port: ${PORT}
********************************************
}

INPUT=$(make_grok_input)
PATTERNS=$(echo grok_exporter*/patterns)
INPUT="$INPUT" PORT=9144 PATTERNS="$PATTERNS" create_grok_yml
sudo iptables -I INPUT -p tcp --dport 9144 -j ACCEPT
./grok_exporter-*/grok_exporter -config grok-exporter.yml&
trap "killall grok_exporter; killall -r process-expor" EXIT

while true
do
  sleep 5
  NEW_INPUT=$(make_grok_input)
  if [ "$NEW_INPUT" != "$INPUT" ]
  then
    echo "Restarting grok-exporter.."
    INPUT="$NEW_INPUT"
    INPUT="$INPUT" PORT=9144 PATTERNS="$PATTERNS" create_grok_yml
    killall grok_exporter
    ./grok_exporter-*/grok_exporter -config grok-exporter.yml&
  fi
done