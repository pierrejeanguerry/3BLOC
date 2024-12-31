import React from 'react';
import { Link } from 'react-router-dom'; 

function Projet() {
  return (
    <div
      className="min-h-screen bg-cover bg-center flex flex-col justify-between"
      style={{
        backgroundImage: "url('Capture d’écran 2024-11-26 104025.png')", 
      }}
    >

      <nav className="flex justify-between items-center p-6 text-white">
        <div className="flex items-center">
          <span className="text-white font-bold text-lg">BlockchainMarketplace</span>
        </div>
        <div className="space-x-6">
          <Link to="/login" className="hover:underline">Log In</Link> 
          <Link to="/sign" className="hover:underline">Sign Up</Link> 
        </div>
      </nav>


      <main className="flex-grow flex items-center justify-start text-white text-left px-24">
        <div>
          <h1 className="text-7xl font-lastica mb-20 uppercase" style={{ marginTop: '-80px' }}>
            Jouets Virtuels
          </h1>

          <p className="text-xl max-w-lg mb-20 leading-relaxed">
            Collectionnez, échangez et explorez des actifs numériques uniques en toute sécurité.
            Plongez dans une expérience rapide et innovante grâce à la blockchain.
          </p>


          <div className="relative flex items-center w-full max-w-sm mt-16">
            <input
              type="text"
              placeholder="Votre identifiant"
              className="w-full px-6 py-4 rounded-full text-gray-900 text-lg focus:outline-none"
            />
            <button className="absolute right-2 px-4 py-4 bg-[#c448d7] rounded-full hover:bg-pink-600">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-6 h-6 text-white"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M21.707 20.293l-5.396-5.396A8.466 8.466 0 0018 10.5C18 5.806 14.194 2 9.5 2S1 5.806 1 10.5 5.806 19 10.5 19c1.66 0 3.212-.499 4.504-1.347l5.396 5.396a1 1 0 001.414-1.414zM10.5 17C6.916 17 4 14.084 4 10.5S6.916 4 10.5 4 17 6.916 17 10.5 14.084 17 10.5 17z" />
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Projet;
