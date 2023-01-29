# coffee-game


### QR reader installation

You need to install ZBar Bar Code Reader http://zbar.sourceforge.net/ and its headers before installing ``zbarlight``.

On Debian
```bash
apt-get install libzbar0 libzbar-dev
pip install zbarlight
```
On Mac OS X

```bash
brew install zbar
export LDFLAGS="-L$(brew --prefix zbar)/lib"
export CFLAGS="-I$(brew --prefix zbar)/include"
pip install zbarlight
```