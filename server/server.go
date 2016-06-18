package main

import (
  "flag"
  "net/http"
  "log"
)

var addr = flag.String("addr", ":8080", "Address at which to listen")

func main() {
  flag.Parse()
  log.Printf("Listening at address %v", *addr)

  http.HandleFunc("/signin", func(w http.ResponseWriter, r *http.Request) {
    log.Println(r.ContentLength)
  })
  log.Fatalln(http.ListenAndServe(*addr, nil))
}
