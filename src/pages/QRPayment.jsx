  function QRPayment() {
    return (
      <div className="page">
        <h2>QR Payment</h2>

        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=payindia" />

        <p>Scan to Pay</p>
      </div>
    );
  }

  export default QRPayment;
