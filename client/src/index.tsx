import { render, h, Component } from 'preact';
import preactLogo from './assets/preact.svg';
import './style.css';

export function App() {
	return (
		<div>
			<a href="https://preactjs.com" target="_blank">
				<img src={preactLogo} alt="Preact logo" height="160" width="160" />
			</a>
			<h1>Get Started building Vite-powered Preact Apps </h1>
			<section>
				<Resource
					title="Test"
					getDescription={() => fetchData()}
					href="https://preactjs.com/tutorial"
				/>
			</section>
		</div>
	);
}

async function fetchData() {
	try {
		const response = await fetch('https://kotaz.ddnsfree.com:24555/api/test');
		const data = await response.text();
		return data;
	} catch (error) {
		console.error('Error fetching data:', error);
		return 'Error fetching data'; // Значение по умолчанию или сообщение об ошибке
	}
}

interface IResourceProps {
	getDescription
	href
	title
}

interface IResourceState {
	description
}

class Resource extends Component<IResourceProps, IResourceState> {
	constructor(props) {
		super(props);
		this.state = {
			description: 'Loading...',
		};
	}

	getDescription() {
		return "No description";
	}

	componentDidMount() {
		this.props.getDescription().then(result => {
			this.setState({ description: result });
		});
	}

	render() {
		return (
			<a href={this.props.href} target="_blank" class="resource">
				<h2>{this.props.title}</h2>
				<p>{this.state.description}</p>
			</a>
		);
	}
}

render(<App />, document.getElementById('app'));