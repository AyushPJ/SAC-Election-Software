import './App.css';

import './App.css';
import { Fragment, Component, createRef } from 'react';
import { Modal, Dropdown, Form, Row, Col } from 'react-bootstrap'
import axios from 'axios'


class AppForm extends Component {
    constructor(props) {
        super(props);
        this.cgpaIP = createRef(null);
        this.statusMsg = "";
        this.state = {
            pickedPosition: "General Secretary",
            positions: [],
            status: "",
            isInvalid: {
                cgpa: false,
                pickedPosition: false,
            }
        };

    }

    componentDidMount() {
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

    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }


    resetState() {
        this.setState({
            pickedPosition: "General Secretary",
            positions: [],
            status: ""

        });
        this.fetchPosts();

    }

    submitForm(e) {
        e.preventDefault();
        axios.post("/applications/submit", { cgpa: this.cgpaIP.current.value, position: this.state.pickedPosition }, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                clearTimeout(this.statusDismiss);
                if (resp.data.msg && resp.data.msg === "accepted") {
                    this.statusMsg = "One of your applications has already been accepted.";
                    this.updateState("status", "fail");
                    this.statusDismiss = setTimeout(() => {
                        this.updateState("status", "");
                    }, 5000);
                }
                else if (resp.data.msg && resp.data.msg === "waiting") {
                    this.statusMsg = "There can only be one standing application waiting for approval.";
                    this.updateState("status", "fail");
                    this.statusDismiss = setTimeout(() => {
                        this.updateState("status", "");
                    }, 5000);
                }
                else {
                    this.statusMsg = "Application submitted successfully.";
                    this.updateState("status", "success");
                    this.props.refetchApps();
                    this.statusDismiss = setTimeout(() => {
                        this.updateState("status", "");
                    }, 5000);
                }
            })
            .catch((error) => {
                console.error(error);
                clearTimeout(this.statusDismiss);
                this.statusMsg = "Something went wrong.";
                this.updateState("status", "fail");
                this.statusDismiss = setTimeout(() => {
                    this.updateState("status", "");
                }, 5000);

            });

    }




    render() {
        const failAlert = <div className="alert alert-danger d-flex align-items-center" role="alert">
            <div>
                {this.statusMsg}
            </div>
        </div>;

        const successAlert = <div className="alert alert-success d-flex align-items-center" role="alert">
            <div>
                {this.statusMsg}
            </div>
        </div>

        let status = "";
        if (this.state.status === "success")
            status = successAlert;
        else if (this.state.status === "fail")
            status = failAlert;

        let dropdownElements = this.state.positions.map((title, index) => {
            return (
                <Dropdown.Item key={index} onClick={(e) => this.updateState("pickedPosition", title)}>{title}</Dropdown.Item>
            )
        });
        if (this.state.positions.length === 0)
            dropdownElements = <Dropdown.Item className="validationElement" disabled><i>Nothing Here</i></Dropdown.Item>;

        return (
            <Modal show={this.props.appFormShow} onHide={() => this.props.setAppFormShow(false)} onExit={() => this.resetState()} id="addTaskModal" size="lg" centered>
                <Modal.Header >
                    <h5 className="modal-title">New Application</h5>
                    <button type="button" className="btn-close" onClick={() => this.props.setAppFormShow(false)}></button>
                </Modal.Header>
                <Modal.Body>

                    <Form noValidate onSubmit={(e) => this.submitForm(e)}>
                        <Form.Group as={Row} className="mb-3" controlId="formPosition">
                            <Form.Label column sm="2">
                                CGPA
                            </Form.Label>
                            <Col sm="10">
                                <Form.Control ref={this.cgpaIP} type="number" defaultValue="0.00" isInvalid={this.state.isInvalid.cgpa} required />
                                <Form.Control.Feedback type="invalid" >
                                    Please enter valid CGPA.
                                </Form.Control.Feedback>
                            </Col>
                        </Form.Group>

                        <Form.Group as={Row} className="mb-3" controlId="formPosition">
                            <Form.Label column sm="2">
                                Position
                            </Form.Label>
                            <Col sm="10">
                                <Dropdown className="validationElement" align="end">
                                    <Dropdown.Toggle variant="btn btn-outline-secondary dropdown-toggle">
                                        {this.state.pickedPosition}
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        {dropdownElements}
                                    </Dropdown.Menu>
                                </Dropdown>
                            </Col>
                        </Form.Group>



                        <span className="formElement">
                            <button type="submit" className="btn btn-primary">Submit</button>
                        </span>
                    </Form>
                    {status}

                </Modal.Body>
            </Modal >
        );
    }
}

export default AppForm;