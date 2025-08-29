script_dir=$(dirname -- "${BASH_SOURCE[0]}")

outfile=false
for arg in "$@"
do
    if [ "${outfile}" = true ]; then
        outfile="${arg}"
    elif [ "${arg}" = "--outfile" ]; then
        outfile=true
    fi
done

if [ "${outfile}" = true ]; then
    echo "Cannot find --outfile."
    exit
elif [ "${outfile}" = false ]; then
    echo "Cannot find --outfile."
    exit
fi

python ${script_dir}/"$@" >> "${outfile}.log" 2>&1
