import logo from './logo.svg';
import './App.css';

import './App.css';
import { Fragment, Component } from 'react';
import { Tab, Tabs, Button, Container, Row, Col } from 'react-bootstrap'
import axios from 'axios'
import AppForm from './AppForm';
import Navbar from './Navbar';

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      applications: {
        accepted: [],
        rejected: [],
        waiting: []
      },
      appFormShow: false,
      key: "waiting"
    };
  }

  componentDidMount() {
    this.fetchApplications();
  }

  updateState(prop, val) {
    let newState = Object.assign({}, this.state);
    newState[prop] = val;
    this.setState(newState);
  }

  fetchApplications() {
    axios.get('/applications/get', { headers: { 'Accept': 'application/json' } })
      .then((resp) => {
        if(resp.data['msg'] !== null && resp.data['msg']==="login-redirect")
          window.location.replace(process.env.REACT_APP_API_SERVER+resp.data['location']);
        this.updateState('applications', resp.data.applications);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  render() {
    let tableElements = [];
    if (this.state.applications) {
      if (this.state.key === "waiting") {
        tableElements = this.state.applications.waiting.map((app, index) => {
          return <tr>
            <td>{app.applicationNo}</td>
            <td>{app.position}</td>
            <td>{app.cgpa}</td>
          </tr>
        });
      }
      else if (this.state.key === "rejected") {
        tableElements = this.state.applications.rejected.map((app, index) => {
          return <tr>
            <td>{app.applicationNo}</td>
            <td>{app.position}</td>
            <td>{app.cgpa}</td>
            <td>{app.adminName}</td>
          </tr>
        });
      }
      else if (this.state.key === "accepted") {
        tableElements = this.state.applications.accepted.map((app, index) => {
          return <tr>
            <td>{app.applicationNo}</td>
            <td>{app.position}</td>
            <td>{app.cgpa}</td>
            <td>{app.adminName}</td>
          </tr>
        });
      }
    }
    return (
      <Fragment>
        <Navbar />
        <Container className="flexApplications">
          <h1>Applications</h1>


          <Button variant="outline-primary" onClick={() => this.updateState("appFormShow", true)}>New Application</Button>
        </Container>
        <AppForm appFormShow={this.state.appFormShow} setAppFormShow={(val) => this.updateState("appFormShow", val)} refetchApps={() => this.fetchApplications()} />
        <Tabs
          fill
          justify
          id="tasks-controlled-tab"
          activeKey={this.state.key}
          onSelect={(k) => this.updateState('key', k)}

        >


          <Tab tabClassName="warning" eventKey="waiting" title="Waiting">

            <div className="container">
              <table className="table table-condensed table-striped">
                <thead>

                  <tr>
                    <th>Application No.</th>
                    <th>Position</th>
                    <th>CGPA</th>
                  </tr>
                </thead>



                <tbody>

                  {tableElements}

                </tbody>

              </table>
            </div>
          </Tab>

          <Tab tabClassName="danger" eventKey="rejected" title="Rejected">
            <div className="container">
              <table className="table table-condensed table-striped">
                <thead>
                  <tr>
                    <th>Application No.</th>
                    <th>Position</th>
                    <th>CGPA</th>
                    <th>Rejected by</th>
                    {/* <th>Remark</th> */}
                  </tr>
                </thead>

                <tbody>

                  {tableElements}

                </tbody>

              </table>
            </div>
          </Tab>
          <Tab tabClassName="success" eventKey="accepted" title="Accepted">
            <div className="container">
              <table className="table table-condensed table-striped">
                <thead>
                  <tr>
                    <th>Application No.</th>
                    <th>Position</th>
                    <th>CGPA</th>
                    <th>Accepted by</th>
                  </tr>
                </thead>

                <tbody>

                  {tableElements}

                </tbody>

              </table>
            </div>
          </Tab>
        </Tabs>
      </Fragment>
    );
  }

}


export default App;
