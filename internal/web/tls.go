package web

import (
	"crypto/tls"
	"net"

	"github.com/pires/go-proxyproto"
	"goauthentik.io/internal/config"
	"goauthentik.io/internal/crypto"
	"goauthentik.io/internal/utils/web"
)

func (ws *WebServer) GetCertificate() func(ch *tls.ClientHelloInfo) (*tls.Certificate, error) {
	cert, err := crypto.GenerateSelfSignedCert()
	if err != nil {
		ws.log.WithError(err).Error("failed to generate default cert")
	}
	return func(ch *tls.ClientHelloInfo) (*tls.Certificate, error) {
		if ws.ProxyServer != nil {
			appCert := ws.ProxyServer.GetCertificate(ch.ServerName)
			if appCert != nil {
				return appCert, nil
			}
		}
		if ws.TenantTLS != nil {
			return ws.TenantTLS.GetCertificate(ch)
		}
		ws.log.Trace("using default, self-signed certificate")
		return &cert, nil
	}
}

// ServeHTTPS constructs a net.Listener and starts handling HTTPS requests
func (ws *WebServer) listenTLS() {
	tlsConfig := &tls.Config{
		MinVersion:     tls.VersionTLS12,
		MaxVersion:     tls.VersionTLS12,
		GetCertificate: ws.GetCertificate(),
	}

	ln, err := net.Listen("tcp", config.G.Web.ListenTLS)
	if err != nil {
		ws.log.WithError(err).Fatalf("failed to listen (TLS)")
		return
	}
	proxyListener := &proxyproto.Listener{Listener: web.TCPKeepAliveListener{TCPListener: ln.(*net.TCPListener)}}
	defer proxyListener.Close()

	tlsListener := tls.NewListener(proxyListener, tlsConfig)
	ws.log.WithField("listen", config.G.Web.ListenTLS).Info("Starting HTTPS server")
	ws.serve(tlsListener)
	ws.log.WithField("listen", config.G.Web.ListenTLS).Info("Stopping HTTPS server")
}
