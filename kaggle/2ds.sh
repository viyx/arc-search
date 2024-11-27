rm -rf temp
mkdir temp
git clone git@github.com:viyx/arc-search.git -b main --single-branch temp
rm arc-search.tar.gz
tar -czf arc-search.tar.gz --directory temp .
rm ~/Downloads/arc-search.tar.gz
mv arc-search.tar.gz ~/Downloads
rm -rf temp