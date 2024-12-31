import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  const [username] = useState('Chris Henderson'); 
  const [isMenuOpen, setIsMenuOpen] = useState(false); 

  const initials = username[0]; 

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen); 
  };

  const handleLogout = () => {
    localStorage.removeItem('token'); 
    window.location.href = '/projet';; 
  };

  return (
    <nav className="bg-black text-white">
      <div className="max-w-screen-xl flex items-center justify-between mx-auto p-4">
        <span className="self-center text-2xl font-semibold whitespace-nowrap">
          BlockchainMarketplace
        </span>

        <div className="flex space-x-8">
          <Link to="/home" className="hover:text-[#E35A47]">
            Home
          </Link>
          <Link to="/boutique" className="hover:text-[#E35A47]">
            Boutique
          </Link>
          <Link to="/actifs" className="hover:text-[#E35A47]">
            Actifs
          </Link>
        </div>

        <div className="relative">
          <button
            onClick={toggleMenu}
            className="w-10 h-10 flex items-center justify-center bg-gray-300 text-black font-bold rounded-full hover:bg-gray-400"
          >
            {initials} 
          </button>

          
          {isMenuOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded shadow-lg">
              <div className="px-4 py-2">
                <span className="font-semibold">Utilisateur :</span>
                <p>{username}</p>
              </div>
              <hr className="border-gray-300" />
              <button
                onClick={handleLogout}
                className="block w-full px-4 py-2 text-left text-red-600 hover:bg-gray-100"
              >
                Se déconnecter
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
