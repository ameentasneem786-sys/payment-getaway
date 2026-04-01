import { useState } from "react";
import API from "../api";
import Toast from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { formatCurrency } from "../utils/formatters";

function SendMoney() {
  const { user, updateUser } = useAuth();
  const [mobile, setMobile] = useState("");
  const [amount, setAmount] = useState("");
  const [popup, setPopup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const nextErrors = {};

    if (!mobile.trim()) {
      nextErrors.mobile = "Mobile number is required";
    } else if (!/^[0-9]{10}$/.test(mobile)) {
      nextErrors.mobile = "Enter a valid 10-digit mobile number";
    }

    if (!amount) {
      nextErrors.amount = "Amount is required";
    } else if (Number.parseFloat(amount) <= 0) {
      nextErrors.amount = "Amount must be greater than 0";
    } else if (Number.parseFloat(amount) > 100000) {
      nextErrors.amount = "Amount cannot exceed 100,000";
    } else if (Number.parseFloat(amount) > Number(user?.balance || 0)) {
      nextErrors.amount = "Amount exceeds available balance";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const sendMoney = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    const parsedAmount = Number.parseFloat(amount);

    try {
      const response = await API.post("/send-money", {
        mobile: mobile.trim(),
        amount: parsedAmount,
      });

      if (response.data.user) {
        updateUser(response.data.user);
      } else {
        updateUser({
          ...user,
          balance: Math.max(0, Number(user?.balance || 0) - parsedAmount),
        });
      }

      if (response.data.message === "Payment Successful") {
        setPopup(true);
        setToast({ message: "Money sent successfully.", type: "success" });

        setTimeout(() => {
          setMobile("");
          setAmount("");
        }, 500);

        setTimeout(() => {
          setPopup(false);
        }, 3000);
      }
    } catch (error) {
      console.error(error);
      setToast({
        message:
          error.response?.data?.error || "Payment failed. Please try again.",
        type: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !loading) {
      sendMoney();
    }
  };

  return (
    <div className="send-container">
      <div className="send-card">
        <h2>Send Money</h2>
        <p style={{ color: "#999", marginBottom: "30px" }}>
          Transfer funds to any mobile number instantly.
        </p>

        <div className="form-group">
          <label>Mobile Number</label>
          <input
            type="tel"
            placeholder="10-digit mobile number"
            value={mobile}
            onChange={(event) => {
              setMobile(event.target.value);
              if (errors.mobile) {
                setErrors({ ...errors, mobile: "" });
              }
            }}
            onKeyDown={handleKeyDown}
            maxLength="10"
            style={{ borderColor: errors.mobile ? "#f44336" : "#e0e0e0" }}
          />
          {errors.mobile && (
            <p style={{ color: "#f44336", fontSize: "0.9rem" }}>
              {errors.mobile}
            </p>
          )}
        </div>

        <div className="form-group">
          <label>Amount</label>
          <input
            type="number"
            placeholder="Enter amount"
            value={amount}
            onChange={(event) => {
              setAmount(event.target.value);
              if (errors.amount) {
                setErrors({ ...errors, amount: "" });
              }
            }}
            onKeyDown={handleKeyDown}
            min="1"
            max="100000"
            style={{ borderColor: errors.amount ? "#f44336" : "#e0e0e0" }}
          />
          {errors.amount && (
            <p style={{ color: "#f44336", fontSize: "0.9rem" }}>
              {errors.amount}
            </p>
          )}
        </div>

        <button
          onClick={sendMoney}
          disabled={loading}
          style={{
            opacity: loading ? 0.6 : 1,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Processing..." : "Send Money"}
        </button>
      </div>

      {popup && (
        <div className="popup">
          <div className="popup-card">
            <h2 style={{ color: "#4caf50" }}>Payment Successful</h2>
            <p style={{ color: "#333", marginBottom: "20px" }}>
              {formatCurrency(amount)} sent to {mobile}
            </p>
            <p style={{ color: "#999", fontSize: "0.9rem" }}>
              Your transaction has been completed successfully.
            </p>
            <button
              onClick={() => setPopup(false)}
              style={{ marginTop: "20px" }}
            >
              Done
            </button>
          </div>
        </div>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

export default SendMoney;
