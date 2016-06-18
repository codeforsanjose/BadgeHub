package main

import (
  "flag"
  "log"
)

var port = flag.Int("port", 8080, "TCP port on which to listen")

func main() {
  flag.Parse()
  log.Printf("Listening on port %d", *port)
}
