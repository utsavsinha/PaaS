#!/bin/bash
read lowerPort upperPort < /proc/sys/net/ipv4/ip_local_port_range
while :; do
    for (( port = lowerPort ; port <= upperPort ; port++ )); do
        nc -l -p "$port" 2>/dev/null && break 2
    done
done