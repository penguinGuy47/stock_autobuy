import React from 'react';

function Footer() {
  return (
    <footer style={footerStyle}>
      <p>© 2024 <a href="https://github.com/penguinGuy47" target="_blank">penguinguy47</a></p>
    </footer>
  );
}

const footerStyle = {
  position: 'fixed',   // Sticks to the bottom
  bottom: '0',
  width: '100%',
  color: '#fff',
  textAlign: 'center',
  padding: '10px'
};

export default Footer;
