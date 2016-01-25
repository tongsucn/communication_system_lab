* Usage

To generate Protocol Buffers files for the Arduino, you need to do following things:

    1. go to ```cproto/nanopb/generator/proto``` and run ```make```
    2. go back and run ```protoc --plugin=protoc-gen-nanopb=cproto/nanopb/generator/protoc-gen-nanopb --nanopb_out=$OUTPUT $SRC```

After generation, copy the generated ```.h```, ```.c``` files and the ```./cproto/nanopb/``` to the Arduino's libraries directory.

P.S. You can find the nanopb [here](https://github.com/nanopb/nanopb.git)
