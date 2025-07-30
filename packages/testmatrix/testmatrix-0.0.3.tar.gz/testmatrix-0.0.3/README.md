## testmatrix

A matrix server sanity tester. Relased under the GNU AGPLv3+

#### Usage

see `python3 testmatrix.py --help`

Credentials are only needed if you want to test an underlying livekit
MatrixRTC setup.

`./testmatrix.py mydomain.com -u @auser:mydomain.com -t mct_COMPATTOKENHERE`

If you have installed the package via pip (or other means), the
installed command will be `testmatrix` and not testmatrix.py.

#### Discussion

[#testmatrix:sspaeth.de](https://matrix.to/#/#testmatrix:sspaeth.de)

#### Installation

Currently, you do not need to install anything, as long as you have all
requirements (see below) installed, you can directly run the testmatrix.py
script.

Alternatively, you can install this by issueing:

`pip install testmatrix`

Or even better: install the cool `uvenv` package manager and do:

`uvenv install testmatrix`

#### Requirements

testmatrix currently requires python3 and python-requests

You can install all requirements on your system by running
`pip install -r requirements.txt`

#### Build an installable package

To build an installable package, you need to have python3-build
installed. Running `python3 -m build` in the git root will create
packages in the `dist` directory.
