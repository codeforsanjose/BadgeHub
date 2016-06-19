# FROM golang:1.6.2-alpine
FROM golang@sha256:11ee357df247baa0fb78818ed92b320e4a026630f305ae12181e0cceddd0fd95
RUN mkdir /go/src/app
WORKDIR /go/src/app
COPY server.go .
EXPOSE 80
CMD ["go", "run", "server.go", "-addr", ":80"]
