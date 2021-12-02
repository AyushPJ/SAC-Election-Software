import './App.css';
import { Fragment, Component } from 'react';
import { Container, Nav, Tab, Col, Row, ToastContainer, Toast } from 'react-bootstrap'
import Navbar from './Navbar';
import AddRemPosts from './AddRemPosts';
import ModVoters from './ModVoters';
import ViewApps from './ViewApps';
import AccessCntl from './AccessCntl';
import ElecStats from './ElecStats';

class AdminPanel extends Component {

  constructor(props) {
    super(props);
    this.state = {
      showToastAlert: false
    };
    this.toastAlertMessage = "";
  }


  updateState(prop, val) {
    let newState = Object.assign({}, this.state);
    newState[prop] = val;
    this.setState(newState);
  }

  setToastAlertMessage(msg) {
    this.toastAlertMessage = msg;
  }

  render() {
    return (
      <Fragment>
        <Navbar />
        <ToastContainer className="p-3 toast-alerts">
          <Toast show={this.state.showToastAlert} onClose={() => this.updateState("showToastAlert", false)} delay={5000} autohide>
            <Toast.Header >
              <strong className="me-auto">{this.toastAlertMessage}</strong>
            </Toast.Header>
          </Toast>
        </ToastContainer>
        <Container className="flexApplications">
          <h1>Admin Panel</h1>

          <Tab.Container id="admin-tabs" defaultActiveKey="elecStats">
            <Row>
              <Col sm={3}>
                <Nav variant="pills" className="flex-column">
                  <Nav.Item>
                    <Nav.Link eventKey="elecStats">Election Statistics</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="accessCntl">Access Control</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="addRemPosts">Add/Remove Posts</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="modVoters">Modify Voters' List</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="viewApps">View Applications</Nav.Link>
                  </Nav.Item>

                </Nav>
              </Col>
              <Col sm={9}>
                <Tab.Content>
                  <Tab.Pane eventKey="elecStats">
                    <ElecStats />
                  </Tab.Pane>
                  <Tab.Pane eventKey="accessCntl">
                    <AccessCntl showToastAlert={this.state.showToastAlert} setShowToastAlert={(val) => this.updateState("showToastAlert", val)} setToastAlertMessage={(msg) => this.setToastAlertMessage(msg)} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="addRemPosts">
                    <AddRemPosts showToastAlert={this.state.showToastAlert} setShowToastAlert={(val) => this.updateState("showToastAlert", val)} setToastAlertMessage={(msg) => this.setToastAlertMessage(msg)} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="modVoters">
                    <ModVoters showToastAlert={this.state.showToastAlert} setShowToastAlert={(val) => this.updateState("showToastAlert", val)} setToastAlertMessage={(msg) => this.setToastAlertMessage(msg)} />
                  </Tab.Pane>
                  <Tab.Pane eventKey="viewApps">
                    <ViewApps showToastAlert={this.state.showToastAlert} setShowToastAlert={(val) => this.updateState("showToastAlert", val)} setToastAlertMessage={(msg) => this.setToastAlertMessage(msg)} />
                  </Tab.Pane>
                </Tab.Content>
              </Col>
            </Row>
          </Tab.Container>
        </Container>
      </Fragment>
    );
  }

}


export default AdminPanel;
