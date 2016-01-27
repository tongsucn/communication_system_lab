# Usage

To generate Protocol Buffers files for the Arduino, you need to do following things:

1. go to `cproto/nanopb/generator/proto and run `make`

2. go back and run `protoc --plugin=protoc-gen-nanopb=cproto/nanopb/generator/protoc-gen-nanopb --nanopb_out=$OUTPUT $SRC`

After generation:

1. create folder named `cproto` under Arduino's library directory

2. copy generated `.h`, `.c` files and all the files under `./cproto` to the created `cproto` in Arduino's libraries directory

3. run `git clone git@github.com:nanopb/nanopb.git` under Arduino's libraries directory to install nanopb runtime for Arduino
