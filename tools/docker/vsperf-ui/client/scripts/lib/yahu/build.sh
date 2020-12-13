# compiles all files with extension .js in current folder into single file called ${foldername}.js outside current folder
cat  $(find . -name "*.js" -type f | xargs echo) > ../${PWD##*/}.js
