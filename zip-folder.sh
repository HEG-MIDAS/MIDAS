#!/bin/bash
for state in media/*; do
    if [ -d "$state" ]; then
        for source in $state/*; do
            if [ -d "$source" ]; then
                if ! [ -z "$(ls $source)" ]; then
                    # Will not run if no directories are available
                    lowerName=$(echo $source| tr '[:upper:]' '[:lower:]')
                    lowerName=$(echo "${lowerName//\//_}")
                    zip -qjr $source/$lowerName".zip" $source/*
                fi
            fi
        done
    fi
done
