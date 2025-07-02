import React from "react";
import logo from "../assests/logo.png";

const Header = () => {
  const handleLogin = () => {
    alert("Login button clicked!");
  };

  return (
    <header className="relative flex justify-between items-center py-3 px-6 bg-white text-gray-600 text-lg font-bold shadow-orange border-b border-orange-100 before:absolute before:bottom-0 before:left-0 before:w-full before:h-[4px] before:bg-gradient-to-r before:from-orange-400 before:to-orange-600">
       <div className="flex items-center">
        <img src={logo} alt="Logo" className="h-9 w-30" />
      </div>

       <button
        className="text-orange-600 hover:text-orange-700 px-4 py-2 text-base font-medium transition-colors duration-200 hover:bg-orange-50 rounded-lg"
        onClick={handleLogin}
      >
        Login
      </button>
    </header>
  );
};

export default Header;


 