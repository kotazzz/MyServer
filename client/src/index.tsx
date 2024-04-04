import { render, createContext } from "preact";
import { useContext, useEffect, useState } from "preact/hooks";

const MyContext = createContext(null);

const apiInfo = {
  base: "https://kotaz.ddnsfree.com:24555/api/",
  endpoints: {
    login: "auth/login",
    test: "auth/test",
    register: "auth/register",
    logout: "auth/logout",
  },
};

function api(endpoint) {
  return apiInfo.base + endpoint;
}

function WelcomeMessage() {
  return (
    <div>
      <h1>Welcome to My App</h1>
      <p>This is a Preact component!</p>
    </div>
  );
}

const Messenger = (props) => {
  const context = useContext(MyContext);

  const logout = async () => {
    try {
      await fetch(api(apiInfo.endpoints.logout), {
        credentials: "include",
        method: "POST",
      });
      context.setIsLoggedIn(false);
    } catch (error) {
      console.error("Ошибка сети:", error);
    }
  };

  return (
    <div>
      <WelcomeMessage />
      <button onClick={logout}>Выйти</button>
    </div>
  );
};

const Login = (props) => {
  const context = useContext(MyContext);
  const [error, setError] = useState("");

  const handleLoginOrRegister = async (url, data) => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
      });

      const result = await response.json();

      if (response.ok) {
        context.setIsLoggedIn(true);
        setError("");
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error("Ошибка сети:", error);
      setError(error.message);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const url =
      event.target.id === "loginForm"
        ? api(apiInfo.endpoints.login)
        : api(apiInfo.endpoints.register);
    handleLoginOrRegister(url, data);
  };

  return (
    <div>
      <h1>Авторизация</h1>
      {error && <div className="error">{error}</div>}
      <LoginForm handleSubmit={handleSubmit} />
      <RegistrationForm handleSubmit={handleSubmit} />
    </div>
  );
};

const LoginForm = ({ handleSubmit }) => (
  <form id="loginForm" onSubmit={handleSubmit}>
    <input
      type="text"
      name="username"
      placeholder="Имя пользователя"
      required
    />
    <br />
    <input
      type="password"
      name="password"
      placeholder="Пароль"
      required
    />
    <br />
    <button type="submit">Вход</button>
  </form>
);

const RegistrationForm = ({ handleSubmit }) => (
  <form id="registrationForm" onSubmit={handleSubmit}>
    <input
      type="text"
      name="username"
      placeholder="Имя пользователя"
      required
    />
    <br />
    <input
      type="password"
      name="password"
      placeholder="Пароль"
      required
    />
    <br />
    <button type="submit">Регистрация</button>
  </form>
);



const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    checkToken();
  }, []);

  const checkToken = async () => {
    try {
      const response = await fetch(api(apiInfo.endpoints.test), {
        credentials: "include",
        method: "POST",
      });
      setIsLoggedIn(response.ok);
    } catch (error) {
      console.error("Ошибка сети:", error);
    }
  };


  return (
    <MyContext.Provider value={{ isLoggedIn, setIsLoggedIn }}>
      {isLoggedIn ? <Messenger /> : <Login />}
    </MyContext.Provider>
  );
};

render(<App />, document.getElementById("app"));
