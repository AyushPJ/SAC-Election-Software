import './App.css';
import { Fragment, Component, createRef } from 'react';
import { Container, Form, Row, Col, FloatingLabel, DropdownButton, Dropdown, Button } from 'react-bootstrap'
import axios from 'axios'

class ViewApps extends Component {

    constructor(props) {
        super(props);
        this.state = {
            applications: [],
            status: [],
            positions: []
        };
        this.postSelectRef = createRef(null);
    }

    componentDidMount() {
        this.fetchApps();
        this.fetchPosts();
    }

    fetchPosts() {
        axios.get("/applications/get-posts", { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                this.updateState("positions", resp.data['posts'])
            })
            .catch((err) => {
                console.error(err);
            })
    }


    fetchApps(post = "All") {
        axios.get("/admin/get-applications/" + post, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                let status = [];
                if (resp.data.applications) {
                    if (resp.data.applications.length === 0) {
                        this.props.setToastAlertMessage("No pending applications.");
                        this.props.setShowToastAlert(true);
                    }
                    else {
                        resp.data.applications.forEach(() => {
                            status.push("waiting");
                        });
                        this.updateState("status", status);
                        
                    }
                    this.updateState("applications", resp.data.applications);
                }
            })
            .catch((err) => {
                console.error(err);
            })
    }

    changeStatus(val, index) {
        let status = this.state.status.slice();
        status[index] = val;
        this.updateState("status", status);
    }

    submitChanges(val) {
        let apps = []

        this.state.applications.forEach((app, index) => {
            if (this.state.status[index] !== "waiting") {
                app["status"] = this.state.status[index];
                apps.push(app);
            }

        });

        axios.post("/admin/change-status", { applications: apps }, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {

                this.props.setToastAlertMessage("Changes saved.");
                this.props.setShowToastAlert(true);
                this.postSelectRef.current.value = "All"
                this.fetchApps("All");

            })
            .catch((err) => {
                this.props.setToastAlertMessage("Something went wrong.");
                this.props.setShowToastAlert(true);
                console.error(err);
            })
    }

    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }


    render() {
        let apps = this.state.applications.map((app, index) => {
            let className = "";
            if (this.state.status[index] === "waiting")
                className = "apps-waiting";
            else if (this.state.status[index] === "accept")
                className = "apps-accept";
            else
                className = "apps-reject";

            return (
                <tr className={className}>
                    <td>{app.applicationNo}</td>
                    <td>{app.rollNo}</td>
                    <td>{app.name}</td>
                    <td>{app.phoneNo}</td>
                    <td>{app.email}</td>
                    <td>{app.position}</td>
                    <td>{app.cgpa}</td>
                    <td>
                        <DropdownButton variant="dark" menuVariant="dark" key={index} id="dropdown-basic-button" title="">
                            <Dropdown.Item onClick={() => this.changeStatus("waiting", index)}>Waiting</Dropdown.Item>
                            <Dropdown.Item onClick={() => this.changeStatus("accept", index)}>Accept</Dropdown.Item>
                            <Dropdown.Item onClick={() => this.changeStatus("reject", index)}>Reject</Dropdown.Item>
                        </DropdownButton>
                    </td>
                </tr>
            );
        });

        let posts = this.state.positions.map((title, index) => {
            return (
                <option key={index} value={title}>{title}</option>
            )
        });

        return (
            <Fragment>
                <Container className="mod-voters-tab">
                    <div className="d-grid gap-2">
                        <Row className="g-2">
                            <Col md={8}>
                                <FloatingLabel controlId="floatingSelectGrid" label="Filter by posts">
                                    <Form.Select ref={this.postSelectRef}>
                                        <option>All</option>
                                        {posts}
                                    </Form.Select>
                                </FloatingLabel>
                            </Col>
                            <Col md={4}>
                                <Button style={{ height: "100%", width: "100%" }} variant="outline-secondary" onClick={() => this.fetchApps(this.postSelectRef.current.value)}>Fetch Applications</Button>
                            </Col>
                        </Row>
                        <Button style={{ height: "100%", width: "100%" }} variant="outline-dark" onClick={() => this.submitChanges()}>Submit Changes</Button>

                    </div>


                    <Container>
                        <table className="table table-condensed">
                            <thead>
                                <tr>
                                    <th>Application No.</th>
                                    <th>Roll No.</th>
                                    <th>Name</th>
                                    <th>Phone No.</th>
                                    <th>NITC Email</th>
                                    <th>Position</th>
                                    <th>CGPA</th>
                                </tr>
                            </thead>
                            <tbody>
                                {apps}
                            </tbody>
                        </table>
                    </Container>
                </Container>
            </Fragment>
        );
    }

}


export default ViewApps;
