import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { toast } from 'react-toastify';
import styled from 'styled-components';
import { saveData, getData, removeData } from '../utils/localStorage';
import '../App.css';


function TradeForm({ action, onRemove, formSessionId  }) {
  const formKey = `tradeForm_${formSessionId }`;

  const [tickers, setTickers] = useState(() => getData(`${formKey}_tickers`) || ['']);
  const [broker, setBroker] = useState(() => getData(`${formKey}_broker`) || '');
  const [quantity, setQuantity] = useState(() => getData(`${formKey}_quantity`) || '');
  const [username, setUsername] = useState(() => getData(`${formKey}_username`) || '');
  const [password, setPassword] = useState(() => getData(`${formKey}_password`) || '');
  const [twoFaCode, setTwoFaCode] = useState(() => getData(`${formKey}_twoFaCode`) || "");
  const [sessionId, setSessionId] = useState(null);
  const [method, setMethod] = useState(null); // 'text', 'captcha_and_text', or 'app'
  const [loading, setLoading] = useState(false);


  // Save form data to localStorage when fields change
  useEffect(() => {
    saveData(`${formKey}_tickers`, tickers);
    saveData(`${formKey}_broker`, broker);
    saveData(`${formKey}_quantity`, quantity);
    saveData(`${formKey}_username`, username);
    saveData(`${formKey}_password`, password);
    saveData(`${formKey}_twoFaCode`, twoFaCode);
  }, [tickers, broker, quantity, username, password, twoFaCode, formKey]);

  const handleTickerChange = (index, value) => {
    const newTickers = [...tickers];
    newTickers[index] = value.toUpperCase();
    setTickers(newTickers);
  };

  const addTickerField = () => {
    setTickers([...tickers, '']);
  };

  const removeTickerField = (index) => {
    const newTickers = [...tickers];
    newTickers.splice(index, 1);
    setTickers(newTickers);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Basic validation
    if (
      (action === 'buy' && tickers.some(ticker => ticker === '')) ||
      (action === 'sell' && !tickers.length) ||
      !broker ||
      !quantity ||
      !username ||
      !password
    ) {
      toast.error('Please fill in all required fields.');
      return;
    }

    // Validation for quantity
    if (!/^\d+$/.test(quantity) || parseInt(quantity) <= 0) {
      toast.error('Please enter a valid quantity.');
      return;
    }

    setLoading(true);
    try {
      const endpoint = action === 'buy' ? '/buy' : '/sell';
      const payload = {
        tickers: tickers,
        broker,
        quantity: parseInt(quantity),
        username,
        password,
      };
      const response = await api.post(endpoint, payload);

      if (response.data.status === 'success') {
        toast.success(`${capitalize(action)} successful.`);
        // resetForm();
      } else if (response.data.status === '2FA_required') {
        setSessionId(response.data.session_id);
        setMethod(response.data.method);
        toast.info('2FA is required.');
      } else {
        toast.error(`${capitalize(action)} failed: ${response.data.message || 'Unknown error.'}`);
        setSessionId(null);
      }
    } catch (error) {
      console.error(`${capitalize(action)} failed:`, error.response ? error.response.data : error.message);
      toast.error(`${capitalize(action)} failed: ${error.response?.data?.error || 'Unknown error.'}`);
    } finally {
      setLoading(false);
    }
  };

  const handle2FASubmit = async (e) => {
    e.preventDefault();

    if ((method === 'text' || method === 'captcha_and_text') && !twoFaCode) {
      toast.error('Please enter the 2FA code.');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        session_id: sessionId,
        two_fa_code: method === 'app' ? null : twoFaCode,
      };

      resetForm()
      const response = await api.post('/complete_2fa', payload);

      if (response.data.status === 'success') {
        toast.success(`${capitalize(action)} successful.`);
      } else {
        toast.error(`${capitalize(action)} failed: ${response.data.message || 'Unknown error.'}`);
      }
    } catch (error) {
      console.error(`${capitalize(action)} failed during 2FA:`, error.response ? error.response.data : error.message);
      toast.error(`${capitalize(action)} failed during 2FA: ${error.response?.data?.error || 'Unknown error.'}`);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTickers(['']);
    setBroker('');
    setQuantity('');
    setUsername('');
    setPassword('');
    setTwoFaCode('');
    setMethod(null);
    removeData(`${formKey}_tickers`);
    removeData(`${formKey}_broker`);
    removeData(`${formKey}_quantity`);
    removeData(`${formKey}_username`);
    removeData(`${formKey}_password`);
    removeData(`${formKey}_twoFaCode`);
  };

  const handleRemoveClick = () => {
    resetForm(); // Reset form
    onRemove();  // Trigger form removal from parent component
  };

  const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  return (
    <FormContainer>
      <FormHeader>
        <FormTitle>{capitalize(action)} Stock</FormTitle>
        <RemoveButton onClick={handleRemoveClick} disabled={loading} aria-label="Remove Form">
          &times;
        </RemoveButton>
      </FormHeader>
      {!sessionId ? (
        <form onSubmit={handleSubmit}>
          {/* Ticker Fields */}
          <FormRow>
            <Label>Ticker Symbol(s)</Label>
            <TickerWrapper>
              {tickers.map((ticker, index) => (
                <TickerContainer key={index}>
                  <TickerInput
                    type="text"
                    placeholder="Ticker"
                    value={ticker}
                    onChange={(e) => handleTickerChange(index, e.target.value)}
                    required
                  />
                  {tickers.length > 1 && (
                    <RemoveTickerButton
                      type="button"
                      onClick={() => removeTickerField(index)}
                      disabled={loading}
                      aria-label="Remove Ticker"
                    >
                      &ndash;
                    </RemoveTickerButton>
                  )}
                  {index === tickers.length - 1 && (
                    <AddTickerButton
                      type="button"
                      onClick={addTickerField}
                      disabled={loading}
                      aria-label="Add Ticker"
                    >
                      +
                    </AddTickerButton>
                  )}
                </TickerContainer>
              ))}
            </TickerWrapper>
          </FormRow>

          {/* Broker Selection */}
          <FormRow>
            <Label>Broker</Label>
            <Select
              value={broker}
              onChange={(e) => setBroker(e.target.value)}
              required
            >
              <option value="">Select Broker</option>
              <option value="chase">Chase</option>
              <option value="fidelity">Fidelity</option>
              <option value="firstrade">First Trade</option>
              <option value="public">Public</option>
              <option value="schwab">Schwab</option>
              <option value="tradier">Tradier</option>
              {/* <option value="webull">Webull</option> */}
              <option value="wells">Wells Fargo</option>
            </Select>
          </FormRow>

          {/* Quantity */}
          <FormRow>
            <Label>Quantity</Label>
            <Input
              type="number"
              placeholder="Quantity"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              min="1"
              required
            />
          </FormRow>

          {/* Username */}
          <FormRow>
           <Label>{broker === 'webull' ? 'Phone Number' : broker === 'public' ? 'Email' : 'Broker Username'}</Label>
            <Input
              type="text"
              placeholder={broker === 'webull' ? 'Phone Number' : broker === 'public' ? 'Email' : 'Broker Username'}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </FormRow>

          {/* Password */}
          <FormRow>
            <Label>Broker Password</Label>
            <Input
              type="password"
              placeholder="Broker Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </FormRow>

          {/* Submit Button */}
          <FormRow>
            <EmptyCell />
            <SubmitButton type="submit" disabled={loading}>
              {loading ? 'Processing...' : capitalize(action)}
            </SubmitButton>
          </FormRow>
        </form>
      ) : (
        <form onSubmit={handle2FASubmit}>
          {method === 'captcha_and_text' && (
            <InfoRow>
              <EmptyCell />
              <InfoText>
                A Captcha has been detected in your trading browser. Please solve it manually in the browser window.
                After solving the Captcha, enter your 2FA code below.
              </InfoText>
            </InfoRow>
          )}
          {method === 'text' && (
            <InfoRow>
              <EmptyCell />
              <InfoText>
                2FA is required. Please enter your 2FA code below.
              </InfoText>
            </InfoRow>
          )}
          {method === 'app' && (
            <InfoRow>
              <EmptyCell />
              <InfoText>
                Approve the 2FA request in your app.
              </InfoText>
            </InfoRow>
          )}

          {(method === 'text' || method === 'captcha_and_text') && (
            <FormRow>
              <Label>2FA Code</Label>
              <Input
                type="text"
                placeholder={`Enter ${capitalize(broker)} 2FA Code`}
                value={twoFaCode}
                onChange={(e) => setTwoFaCode(e.target.value)}
                required
              />
            </FormRow>
          )}

          {/* Submit button label changes based on the method */}
          <FormRow>
            <EmptyCell />
            <SubmitButton type="submit" disabled={loading}>
              {loading ? (method === 'app' ? 'Approving...' : 'Submitting...') : (method === 'app' ? 'Approve 2FA' : 'Submit 2FA Code')}
            </SubmitButton>
          </FormRow>
        </form>
      )}
    </FormContainer>
  );
}

const FormContainer = styled.div`
  background-color: #2c2c2c;
  padding: 1.5rem;
  border: 1px solid #444;  /* Dark border */
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.8);
  width: 100%;
  max-width: 300px; 
  box-sizing: border-box;
  color: #ffffff;  /* White text */
`;

const FormHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const FormTitle = styled.h3`
  margin: 0;
  font-size: 1.25rem;
  color: #C4DAD2;
`;

const RemoveButton = styled.button`
  background-color: #E85C0D;
  color: white;
  border: none;
  font-size: 1.2rem;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  
  &:hover {
    background-color: #800000;
  }
`;

const FormRow = styled.div`
  display: contents;
`;

const Label = styled.label`
  font-weight: bold;
  color: #bbbbbb;
  margin-bottom: 0.5rem;
  display: block;
`;

const EmptyCell = styled.div``;

const Input = styled.input`
  padding: 0.6rem;
  border: 1px solid #555555;
  border-radius: 4px;
  background-color: #444444;
  color: #ffffff;  /* White text */
  width: 100%;
  box-sizing: border-box;
`;

const Select = styled.select`
  padding: 0.6rem;
  border: 1px solid #555555;  /* Darker select borders */
  border-radius: 4px;
  background-color: #444444;  /* Dark select background */
  color: #ffffff;  /* White text */
  width: 100%;
  box-sizing: border-box;
`;

const TickerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const TickerContainer = styled.div`
  display: flex;
  align-items: center;
`;

const TickerInput = styled.input`
  flex: 1;
  padding: 0.6rem;
  border: 1px solid #555555;
  border-radius: 4px;
  color: white;
  background-color: #444444;
`;

const AddTickerButton = styled.button`
  margin-left: 0.5rem;
  padding: 0.6rem;
  background-color: #08C2FF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #006BFF;
  }
`;

const RemoveTickerButton = styled.button`
  margin-left: 0.5rem;
  padding: 0.6rem;
  background-color: #982B1C;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #800000;
  }
`;

const SubmitButton = styled.button`
  margin-top: 10px;
  padding: 0.5rem;
  background-color: #4E9F3D;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #1E5128;
  }
`;

const InfoRow = styled.div`
  display: contents;
`;

const InfoText = styled.p`
  color: #555555;
  font-size: 0.95rem;
  margin: 0;
`;

export default TradeForm;
