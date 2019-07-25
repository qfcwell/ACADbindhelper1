package main

import (
    "fmt"
    "log"
    "net"
    "net/rpc/jsonrpc"
	"net/rpc"
	"os"
	"encoding/json"
)

//配置文件
type Configuration struct {
	Listen_addr string
    Arx_path string
	Lsp_path string
	EmptyDwg string
	RemoveProxy_dll string
    ACSPath_dict map[string]string
    Server_dict map[string][4]string
    Method map[string]int
    Server map[string]string
    Exception_list [][5]string
}

type ACADBindhelper struct{}

func (c ACADBindhelper)GetConfig(req *string,res *Configuration) error{
	fmt.Println("Receive Call for Function: Get_Configuration")
	*res = conf
	return nil
}

func Load_config(path string) Configuration{
    file, _ := os.Open(path)
    defer file.Close()
    decoder := json.NewDecoder(file)
    conf := Configuration{}
    err := decoder.Decode(&conf)
    if err != nil {
    	fmt.Println(decoder)
        fmt.Println("Error:", err)
    }
    return conf
}
 
var conf Configuration = Load_config("config.json")

func main() {
	log.Print("Starting Server...")
	l, err := net.Listen("tcp", conf.Listen_addr)
	defer l.Close()
	if err != nil {log.Fatal(err)}
	log.Print("listening on: ", l.Addr())
	rpc.Register(new (ACADBindhelper))
	for {
		conn, err := l.Accept()
		if err != nil {
			log.Printf("accept error: %s", conn)
			continue
		}
		log.Printf("connection started: %v", conn.RemoteAddr())
		go jsonrpc.ServeConn(conn)
	}
}


