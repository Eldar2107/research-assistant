import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Home.module.scss';

const Home = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null); // Backend-dən gələn cavab üçün
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsLoading(true);
    
    try {
      // FastAPI backend-inə POST sorğusu
      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error('Server xətası baş verdi!');
      }

      const data = await response.json();
      setResult(data);
      console.log("Backend-dən gələn cavab:", data);
      
    } catch (error) {
      console.error("Xəta:", error);
      alert("Axtarış zamanı xəta baş verdi. Zəhmət olmasa backend serverinin işlədiyini yoxlayın.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.homeContainer}>
      
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
            <Link to="/" className={styles.active}>Ana Səhifə</Link>
            <Link to="/about">Haqqında</Link>
          </div>
        </div>
      </nav>

      {/* Əsas Ekran */}
      <main className={styles.mainContent}>
        
        {/* Sol tərəf - Axtarış */}
        <section className={styles.searchSection}>
          <div className={styles.contentWrapper}>
            <h1>
              Araşdırmaq istədiyiniz <br />
              <span className={styles.highlight}>mövzunu yazın</span>
            </h1>
            <p>Süni intellekt Wikipedia, arXiv və veb mənbələrini sizin üçün eyni anda analiz edəcək.</p>

            <form className={styles.searchForm} onSubmit={handleSearch}>
              <input
                type="text"
                placeholder="Deep Learning nədir?..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? "Axtarılır..." : "Araşdır"}
              </button>
            </form>
          </div>
        </section>

        {/* Sağ tərəf - Vektor Robot Şəkli */}
        <section className={styles.imageSection}>
          <div className={styles.bgBlob}></div>
          <img src="/robot.svg" alt="AI Robot" className={styles.robotImg} />
        </section>

      </main>
    </div>
  );
};

export default Home;