# Source Routing

```
                 
                   
                   +--+
            +------+s2+------+
            |      +--+      |
+--+      +-++              ++-+       +--+
|h1+------+s1|              |s4+-------+h2|
+--+      +-++              ++-+       +--+
            |                |
            |      +--+      |
            +------+s3+------+
                   +--+

         
```

## Introduction

I modified the Simple INT and Source Routing examples from the [P4-Learning Repo](https://github.com/nsg-ethz/p4-learning/tree/master/examples).

## How to run

To run this implementation, you need to have [P4-Util VM](https://nsg-ethz.github.io/p4-utils/installation.html).

```bash
sudo python network.py
```

Start the receiver script at `h2`:
```bash
mx h2
python receive.py
```


Send packets with the source routing header indicating which path the packet has
to take. Once you start the script it will ask you which path do you want to take.

You can decide to go to `h2` through `s2` and `s4`:

```bash
mx h1
python send.py 10.0.4.2 "Hello, h2!"
Type space separated switch_ids nums (example: "2 3 2 2 1") or "q" to quit: 2 4
```

Or you can use `s3` instead:

```bash
python send.py 10.0.4.2 "Hello, h2!"
Type space separated switch_ids nums (example: "2 3 2 2 1") or "q" to quit: 3 4
```

You can also do some loops:

```bash
python send.py 10.0.4.2 "Hello, h2!"
Type space separated switch_ids nums (example: "2 3 2 2 1") or "q" to quit: 2 4 3 1 2 4
```

This implementation supports maximum 9 hops.