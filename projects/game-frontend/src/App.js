import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './Componenent/NavBar';
import Home from './Pages/Home';
import Boutique from './Pages/Boutique';
import Actifs from './Pages/Actifs';
import Projet from './Pages/Projet';
import Login from './Pages/Login';
import Sign from './Pages/Sign'

const App = () => {
  return (
    <Router>
      <div>
        {/* Condition pour afficher la NavBar sur toutes les pages sauf /projet et /login */}
        {window.location.pathname !== '/projet' && window.location.pathname !== '/login' && window.location.pathname !== '/sign' && <NavBar />}
        <Routes></Routes>
        <Routes>
          <Route path="/projet" element={<Projet />} />
          <Route path="/home" element={<Home />} />
          <Route path="/boutique" element={<Boutique />} />
          <Route path="/actifs" element={<Actifs />} />
          <Route path="/login" element={<Login />} />
          <Route path="/sign" element={<Sign />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;