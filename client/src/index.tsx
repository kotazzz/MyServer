import { h, Component, render } from 'preact';
import { useState, useEffect } from 'preact/hooks';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [error, setError] = useState('');

    // Проверка токена при загрузке страницы
    useEffect(() => {
        const checkToken = async () => {
            try {
                const response = await fetch('https://kotaz.ddnsfree.com:24555/api/auth/test', {
                    credentials: 'include',
                });
                if (response.ok) {
                    setIsLoggedIn(true);
                } else {
                    setIsLoggedIn(false);
                }
            } catch (error) {
                console.error('Ошибка сети:', error);
            }
        };

        checkToken();
    }, []);

    const handleLoginOrRegister = async (url, data) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                credentials: 'include',
            });

            const result = await response.json();

            if (response.ok) {
                setIsLoggedIn(true);
                setError('');
            } else {
                setError(result.message);
            }
        } catch (error) {
            console.error('Ошибка сети:', error);
            setError(error.message);
        }
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        const url = event.target.id === 'loginForm' ? 'https://kotaz.ddnsfree.com:24555/api/auth/login' : 'https://kotaz.ddnsfree.com:24555/api/auth/register';
        handleLoginOrRegister(url, data);
    };

    const handleLogout = async () => {
        try {
            await fetch('https://kotaz.ddnsfree.com:24555/api/auth/logout', {
                credentials: 'include',
            });
            setIsLoggedIn(false);
        } catch (error) {
            console.error('Ошибка сети:', error);
        }
    };

    const handleSecret = async () => {
        try {
            const response = await fetch('https://kotaz.ddnsfree.com:24555/api/secret', {
                credentials: 'include',
            });

            if (response.ok) {
                const result = await response.text();
                alert(result);
            } else {
                setIsLoggedIn(false);
            }
        } catch (error) {
            console.error('Ошибка сети:', error);
            setIsLoggedIn(false);
        }
    };

    if (!isLoggedIn) {
        return (
            <div>
                <h1>Авторизация</h1>
                {error && <div className="error">{error}</div>}
                <form id="loginForm" onSubmit={handleSubmit}>
                    <input type="text" name="username" placeholder="Имя пользователя" required /><br />
                    <input type="password" name="password" placeholder="Пароль" required /><br />
                    <button type="submit">Вход</button>
                </form>
                <form id="registrationForm" onSubmit={handleSubmit}>
                    <input type="text" name="username" placeholder="Имя пользователя" required /><br />
                    <input type="password" name="password" placeholder="Пароль" required /><br />
                    <button type="submit">Регистрация</button>
                </form>
            </div>
        );
    }

    return (
        <div>
            <h1>Добро пожаловать!</h1>
            <button onClick={handleSecret}>Получить секрет</button>
            <button onClick={handleLogout}>Выход</button>
        </div>
    );
}

render(<App />, document.getElementById('app'));
