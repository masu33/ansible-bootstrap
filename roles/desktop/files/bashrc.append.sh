if [[ $- != *i* ]] ; then
  # shell is non-interactive. be done now!
  return
fi

# Load all files from .shell/bashrc.d directory
if [ -d $HOME/.bashrc.d ]; then
  for file in `ls $HOME/.bashrc.d`; do
    source $file
  done
fi
