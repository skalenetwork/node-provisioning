#!/bin/bash

while :
    do
        nodeID=$(cat /root/.skale/node_data/node_config.json | jq -r '.node_id')
        schains=($(ls /root/.skale/node_data/schains/))
        skaledPorts=()
        for i in ${schains[@]}; do
            nodeOrder=($(cat /root/.skale/node_data/schains/$i/schain_$i.json | jq -r '.skaleConfig.sChain.nodes' | jq '.[] .nodeID'))
            ports=($(cat /root/.skale/node_data/schains/$i/schain_$i.json | jq -r '.skaleConfig.sChain.nodes' | jq '.[] .httpRpcPort'))
            for y in "${!nodeOrder[@]}"; do
                if [[ "${nodeOrder[$y]}" = "${nodeID}" ]]; then
                break
                fi
            done
            skaledPorts+=(${ports[y]})
        done
        for i in {1..30}; do
                echo '{' > /root/.skale_stats/data/metrics.json
                for i in "${!skaledPorts[@]}"; do
                    schains[$i]=$(echo "${schains[$i]}" | tr - _)
                    echo $'\t"'${schains[i]}'":{},'>> /root/.skale_stats/data/metrics.json
                    curl -X POST --data '{"jsonrpc":"2.0","method":"skale_stats","params":null,"id":1205}' 127.0.0.1:${skaledPorts[i]} > /root/.skale_stats/data/${schains[i]}.json
                    done
                sed -i '$ s/.$//' /root/.skale_stats/data/metrics.json
                echo $'}' >> /root/.skale_stats/data/metrics.json
                for i in "${!skaledPorts[@]}"; do
                    schain=$( cat /root/.skale_stats/data/${schains[i]}.json )
                    jq ".\"${schains[i]}\" += $schain" /root/.skale_stats/data/metrics.json > /root/.skale_stats/data/metrics.json.tmp && mv /root/.skale_stats/data/metrics.json.tmp /root/.skale_stats/data/metrics.json
                    done
                echo "SUCCESS STATS DUMP"
                jq -r 'paths(scalars) as $p  | [ ( [ $p[] | tostring ] | join("_") ), ( getpath($p) | tojson )] | join(" ")' /root/.skale_stats/data/metrics.json | tr -d '"' > /var/www/html/metrics
                gawk -i inplace '!/result_executionPerformance_RPC_protocols_HTTP_method/' /var/www/html/metrics
                gawk -i inplace '!/result_executionPerformance_RPC_protocols_HTTPS_method/' /var/www/html/metrics
                gawk -i inplace '!/result_executionPerformance_RPC_summary_method/' /var/www/html/metrics
                gawk -i inplace '!/result_executionPerformance_RPC_summary_protocol/' /var/www/html/metrics
                gawk -i inplace '!/result_unddos_calls/' /var/www/html/metrics
                sleep 5
            done
    done