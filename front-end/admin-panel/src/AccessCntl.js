import './App.css';
import { Fragment, Component, createRef } from 'react';
import { Container, Form, Row, Col, FloatingLabel, Button } from 'react-bootstrap'
import axios from 'axios'

class AccessCntl extends Component {

    constructor(props) {
        super(props);
        this.state = {
            open: false,
            method: null,
            autoSetApp: false,
            autoSetVote: false,
            appStatus: null,
            votingStatus: null,
            currentDT: null
        };
        this.manualSwitchRef = createRef(null);
        this.autoAppOpen = createRef(null);
        this.autoAppClose = createRef(null);
        this.autoVoteOpen = createRef(null);
        this.autoVoteClose = createRef(null);
    }

    componentDidMount() {
        this.fetchSiteStatus();
        this.updateState('currentDT', new Date().toISOString().substring(0,16));
    }

    fetchSiteStatus() {
        axios.get("/admin/get-site-status", { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                if (resp.data.applications && resp.data.voting) {
                    this.updateState("appStatus", resp.data.applications);
                    this.updateState("votingStatus", resp.data.voting);
                }
            })
            .catch((err) => {
                console.error(err);
            })
    }


    submitChanges() {
        let method = this.state.method;
        if (this.state.open) {
            if (method === "manual") {
                let toOpen = null;
                if (this.manualSwitchRef.current.checked)
                    toOpen = "voting";
                else
                    toOpen = "applications";

                axios.post("/admin/change-site-status", { method: method, toOpen: toOpen }, { headers: { 'Accepts': 'application/json' } })
                    .then((resp) => {

                        this.props.setToastAlertMessage("Changes saved.");
                        this.props.setShowToastAlert(true);
                        this.fetchSiteStatus();

                    })
                    .catch((err) => {
                        this.props.setToastAlertMessage("Something went wrong.");
                        this.props.setShowToastAlert(true);
                        console.error(err);
                    })
            }
            else if (method === "automatic") {
                let appOpen = null;
                let appClose = null;
                let voteOpen = null;
                let voteClose = null;
                if (this.state.autoSetApp) {
                    appOpen = this.autoAppOpen.current.value;
                    if (appOpen)
                        appOpen = new Date(appOpen).toISOString();
                    appClose = this.autoAppClose.current.value;
                    if (appClose)
                        appClose = new Date(appClose).toISOString();
                }
                if (this.state.autoSetVote) {
                    voteOpen = this.autoVoteOpen.current.value;
                    if (voteOpen)
                        voteOpen = new Date(voteOpen).toISOString();

                    voteClose = this.autoVoteClose.current.value;
                    if (voteClose)
                        voteClose = new Date(voteClose).toISOString();

                }

                axios.post("/admin/change-site-status", { method: method, appOpen: appOpen, appClose: appClose, voteOpen: voteOpen, voteClose: voteClose }, { headers: { 'Accepts': 'application/json' } })
                    .then((resp) => {
                        if (resp.data.msg) {
                            this.props.setToastAlertMessage(resp.data.msg);
                            this.props.setShowToastAlert(true);
                            this.fetchSiteStatus();
                        }
                        else {
                            this.props.setToastAlertMessage("Changes saved.");
                            this.props.setShowToastAlert(true);
                            this.fetchSiteStatus();
                        }

                    })
                    .catch((err) => {
                        this.props.setToastAlertMessage("Something went wrong.");
                        this.props.setShowToastAlert(true);
                        console.error(err);
                    })
            }
        }
        else {

            axios.post("/admin/change-site-status", { method: "close" }, { headers: { 'Accepts': 'application/json' } })
                .then((resp) => {
                    this.props.setToastAlertMessage("Changes saved.");
                    this.props.setShowToastAlert(true);
                    this.fetchSiteStatus();

                })
                .catch((err) => {
                    this.props.setToastAlertMessage("Something went wrong.");
                    this.props.setShowToastAlert(true);
                    console.error(err);
                })
        }

    }


    resetForm(val) {
        let newState = Object.assign({}, this.state);
        newState['open'] = val;
        newState['method'] = null;
        this.setState(newState);
    }






    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }


    render() {
        let methods = null;
        let manual = null;
        let automatic = null;
        if (this.state.open) {
            methods = <div className="flex-col-space-between" style={{ fontSize: "large" }}>
                <Form.Check
                    inline
                    label="Open manually"
                    name="group1"
                    type="radio"
                    onClick={(e) => { this.updateState("method", "manual") }}
                />
                <Form.Check
                    inline
                    label="Open automatically"
                    name="group1"
                    type="radio"
                    onClick={(e) => { this.updateState("method", "automatic") }}
                />
            </div>
            if (this.state.method === "manual") {
                manual = <Fragment>
                    <div className="flex-col-space-evenly" style={{ fontSize: "x-large" }}>
                        <Form.Label className="manual-app-text">Applications</Form.Label>
                        <Form.Switch onMouseDown={(e) => e.preventDefault()} className="form-switch-md" variant="outline-dark" ref={this.manualSwitchRef}></Form.Switch>
                        <Form.Label className="manual-vote-text">Voting</Form.Label>

                    </div>

                </Fragment>
            }
            else if (this.state.method === "automatic") {
                let setApp = null;
                let setVote = null;
                if (this.state.autoSetApp)
                    setApp = <Fragment>
                        <FloatingLabel
                            label="Opening Datetime"
                            className="mb-2"
                        >
                            <Form.Control ref={this.autoAppOpen} type="datetime-local" min={this.state.currentDT}/>
                        </FloatingLabel>
                        <FloatingLabel label="Closing Datetime">
                            <Form.Control ref={this.autoAppClose} type="datetime-local" min={this.state.currentDT}/>
                        </FloatingLabel>
                    </Fragment>;

                if (this.state.autoSetVote)
                    setVote = <Fragment>
                        <FloatingLabel
                            label="Opening Datetime"
                            className="mb-2"
                        >
                            <Form.Control ref={this.autoVoteOpen} type="datetime-local" min={this.state.currentDT}/>
                        </FloatingLabel>
                        <FloatingLabel label="Closing Datetime">
                            <Form.Control ref={this.autoVoteClose} type="datetime-local" min={this.state.currentDT}/>
                        </FloatingLabel>
                    </Fragment>;
                automatic = <Fragment>
                    <div>
                        <Row>
                            <Col>
                                <Form.Check
                                    inline
                                    label="Set application window"
                                    name="application-window"
                                    type="checkbox"
                                    onClick={(e) => { this.updateState("autoSetApp", e.target.checked) }}
                                />
                                {setApp}
                            </Col>
                            <Col>
                                <Form.Check
                                    inline
                                    label="Set voting window"
                                    name="voting-window"
                                    type="checkbox"
                                    onClick={(e) => { this.updateState("autoSetVote", e.target.checked) }}
                                />
                                {setVote}
                            </Col>
                        </Row>
                    </div>
                </Fragment>;
            }
        }

        let appStatus = this.state.appStatus;

        let votingStatus = this.state.votingStatus;
        if (appStatus) {
            if (!appStatus.status)
                appStatus = <div>Closed</div>;
            else if (appStatus.status === "Automatic") {
                let open = null;
                let close = null;
                if (appStatus.open)
                    open = new Date(appStatus.open).toLocaleString();
                else
                    open = "not defined"
                if (appStatus.close)
                    close = new Date(appStatus.close).toLocaleString();
                else
                    close = "not defined"
                appStatus = <Fragment>
                    <div>Automatic</div>
                    <div>{"Open: " + open}</div>
                    <div>{"Close: " + close}</div>
                </Fragment>;
            }
            else if (appStatus.status)
                appStatus = <div>Open</div>
        }
        if (votingStatus) {
            if (!votingStatus.status)
                votingStatus = <div>Closed</div>;
            else if (votingStatus.status === "Automatic") {
                let open = null;
                let close = null;
                if (votingStatus.open)
                    open = new Date(votingStatus.open).toLocaleString();
                else
                    open = "not defined"
                if (votingStatus.close)
                    close = new Date(votingStatus.close).toLocaleString();
                else
                    close = "not defined"
                votingStatus = <Fragment>
                    <div>Automatic</div>
                    <div>{"Open: " + open}</div>
                    <div>{"Close: " + close}</div>
                </Fragment>;
            }
            else if (votingStatus.status)
                votingStatus = <div>Open</div>
        }
        return (
            <Container className="access-cntl-tab">
                <div>
                    <div style={{ fontSize: "x-large" }}>Current Site Status</div>

                    <Row>
                        <Col>
                            <div><b>Applications Page:</b></div>
                            {appStatus}
                        </Col>
                        <Col>
                            <div><b>Voting Page</b></div>
                            {votingStatus}
                        </Col>
                    </Row>
                </div>
                <Button style={{ height: "100%", width: "100%" }} variant="outline-dark" onClick={() => this.submitChanges()}>Save Changes</Button>

                <div className="flex-col-space-between" style={{ fontSize: "x-large" }}>
                    <Form.Label >Open access to students</Form.Label>
                    <Form.Switch className="form-switch-lg" variant="outline-dark" onClick={(e) => { this.resetForm(e.target.checked)}}></Form.Switch>
                </div>
                {methods}
                {manual}
                {automatic}

            </Container>
        );
    }

}


export default AccessCntl;
