pushd downloads
item_list='c cpp python java php javascript'
for item in $item_list
do
   if [ -d $item ]
   then
      echo -n "$item "
      ls $item | wc -l
   fi
done

du -shc $item_list
popd
