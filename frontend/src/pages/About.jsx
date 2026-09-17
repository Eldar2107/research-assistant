import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './About.module.scss';

const About = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.aboutContainer}>
      
      {/* Menyu */}
      <nav className={styles.navbar}>
        <div className={styles.navContainer}>
          <div className={styles.logo} onClick={() => navigate('/')}>
            <img src="/robot.svg" alt="Logo Robot" className={styles.logoImg} />
            <span className={styles.title}>
              <span className={styles.naicText}>NAIC</span> <span className={styles.researchText}>Research</span>
            </span>
          </div>
          <div className={styles.navLinks}>
            <Link to="/">Ana Səhifə</Link>
            <Link to="/about" className={styles.active}>Haqqında</Link>
          </div>
        </div>
      </nav>

      {/* Haqqında Məzmunu */}
      <main className={styles.mainContent}>
        <div className={styles.contentWrapper}>
          <h1>
            Layihə Haqqında <br />
            <span className={styles.highlight}>AI Academy Final Layihəsi</span>
          </h1>
          <p>
            <strong>NAIC Research</strong> — AI Academy-nin Software Engineering proqramı çərçivəsində 3 nəfərlik komandamız tərəfindən hazırlanan final layihəsidir. Bu platforma akademik məqalələri, Wikipedia verilənlərini və qlobal veb mənbələrini saniyələr içində eyni anda analiz edib sintez edən süni intellekt əsaslı axtarış və orkestratsiya sistemidir.
          </p>

          <div className={styles.featuresGrid}>

            <div className={styles.featureCard}>
              <h3>Multi-Source Analysis</h3>
              <p>Məlumatları arXiv, Wikipedia və digər etibarlı bazalardan paralel şəkildə toplayıb emal edir.</p>
            </div>
            <div className={styles.featureCard}>
              <h3>Müasir Texnologiyalar</h3>
              <p>React, Vite, SCSS, Python və FastAPI üzərində qurulan yüksək performanslı və müasir arxitektura.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About;