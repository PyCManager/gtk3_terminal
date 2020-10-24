# Terminal  
  
This is a terminal in gtk3 developed with python. Testing how to do it for the moment.  
  
As I use shortcuts as "Alt + Arrow, with nothing configured, I have some characters  
printed in the terminal when I open or switch between tabs. To circumvent this problem  
I have provided two files for zsh and bash:  
For zsh, add to your ~/.zshrc the binds provided in the zshrc.  
If you use bash, copy the inputrc as ~/.inputrc  
These bindings will not be much of use if you use other shortcuts combinations.  

```shell
# This one is required, but should already be installed
sudo apt-get install python-gobject

# Installing this will install the
# notify-send program. Check that out
# for sending notifications in the shell
sudo apt-get install libnotify-bin

# The development headers if you
# want to do any development in C/C++
sudo apt-get install libnotify-dev
```
[Install libnotify on MacOS](https://brewinstall.org/Install-libnotify-on-Mac-with-Brew)