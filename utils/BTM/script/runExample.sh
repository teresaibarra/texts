#!/bin/bash
# run an toy example for BTM

K=30   # number of topics

alpha=`echo "scale=3;50/$K"|bc`
beta=0.03
niter=500
# save_step=501

# Get the directory of the currently running script
script_dir=$(dirname "$0")

input_dir="${script_dir}/../model_input/"
output_dir="${script_dir}/../model_output/"
model_dir="${output_dir}model/"
mkdir -p "$output_dir/model"

# the input docs for training
doc_pt="${input_dir}messages.txt"

echo "=============== Index Docs ============="
# docs after indexing
dwid_pt="${output_dir}doc_wids.txt"
# vocabulary file
voca_pt="${output_dir}voca.txt"
python "${script_dir}/indexDocs.py" "$doc_pt" "$dwid_pt" "$voca_pt"

## learning parameters p(z) and p(w|z)
echo "=============== Topic Learning ============="
W=$(wc -l < "$voca_pt") # vocabulary size
make -C "${script_dir}/../src"
"${script_dir}/../src/btm" est "$K" "$W" "$alpha" "$beta" "$niter" "$save_step" "$dwid_pt" "$model_dir"

# infer p(z|d) for each doc
echo "================ Infer P(z|d)==============="
"${script_dir}/../src/btm" inf sum_b "$K" "$dwid_pt" "$model_dir"

## output top words of each topic
echo "================ Topic Display ============="
python "${script_dir}/topicDisplay.py" "$model_dir" "$K" "$voca_pt"