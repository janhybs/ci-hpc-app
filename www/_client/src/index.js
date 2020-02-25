import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';
import registerServiceWorker from './_old/registerServiceWorker';

import 'bootstrap/dist/css/bootstrap.css';
import 'font-awesome/css/font-awesome.min.css';
import './styles/index.css';
import './styles/table.css';
import './styles/diff.css';
import './styles/loading.css';
import 'animate.css/animate.min.css';

import ReactNotification from 'react-notifications-component';
import 'react-notifications-component/dist/theme.css';

const baseUrl = document.getElementsByTagName('base')[0].getAttribute('href');
const rootElement = document.getElementById('root');

ReactDOM.render(
  <BrowserRouter basename={baseUrl}>
    <>
      <ReactNotification />
      <App />
    </>
  </BrowserRouter>,
  rootElement);

registerServiceWorker();

