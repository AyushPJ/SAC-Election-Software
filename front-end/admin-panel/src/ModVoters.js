import './App.css';
import { Fragment, Component, createRef } from 'react';
import { Container, InputGroup, FormControl, Button } from 'react-bootstrap'
import axios from 'axios'

class ModVoters extends Component {

    constructor(props) {
        super(props);
        this.state = {
            student: null
        };
        this.rollNoIP = createRef(null);
    }


    fetchStudent() {
        axios.post("/admin/fetch-student", {rollNo: this.rollNoIP.current.value}, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                if(resp.data.msg && resp.data.msg==="Does not exist"){
                    this.props.setToastAlertMessage("Student does not exist.");
                    this.props.setShowToastAlert(true);

                }
                else { 
                    this.updateState("student", resp.data.student);
                }
            })
            .catch((err) => {
                console.error(err);
            })
    }

    changeEligibility(val) {
        axios.post("/admin/change-eligibility", { rollNo: this.state.student.rollNo, eligibility: val }, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                if(val)
                    this.props.setToastAlertMessage("Student "+this.state.student.rollNo+" is now eligible.");
                else
                this.props.setToastAlertMessage("Student "+this.state.student.rollNo+" is now ineligible.");

                this.props.setShowToastAlert(true);
                this.updateState("student", null);
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
        let studentDetails = null;
        let changeEligibilityButton = null;
        if(this.state.student) {
            let eligibilityStatus = null;
            if(this.state.student.eligibility){
                eligibilityStatus = <td style={{color: "green"}}>eligible</td>
                changeEligibilityButton = <Button variant="outline-danger" onClick={()=>this.changeEligibility(false)}>Mark as ineligible</Button>
            }
            else {
                eligibilityStatus = <td style={{color: "red"}}>ineligible</td>
                changeEligibilityButton = <Button variant="outline-success" onClick={()=>this.changeEligibility(true)}>Mark as eligible</Button>
            }
            studentDetails = <Container>
                <table className="table table-condensed">
                    <tbody>
                        <tr>
                            <td>Roll No.</td>
                            <td>{this.state.student.rollNo}</td>
                        </tr>
                        <tr>
                            <td>Name</td>
                            <td>{this.state.student.name}</td>
                        </tr>
                        <tr>
                            <td>NITC Email</td>
                            <td>{this.state.student.email}</td>
                        </tr>
                        <tr>
                            <td>Phone No.</td>
                            <td>{this.state.student.phoneNo}</td>
                        </tr>
                        <tr>
                            <td>Eligibility</td>
                            <td>{eligibilityStatus}</td>
                        </tr>
                    </tbody>
                </table>
            </Container>
        }
        return (
            <Fragment>
                <Container className="mod-voters-tab">
                    <InputGroup className="mb-3">
                        <FormControl
                            placeholder="Enter roll no. of student here" ref={this.rollNoIP}
                        />
                        <Button variant="outline-secondary" id="fetch-student-button" onClick={() => this.fetchStudent()}>
                            Get student
                        </Button>
                    </InputGroup>
                    {studentDetails}
                    <div style={{textAlign: "right"}}>
                    {changeEligibilityButton}
                    </div>
                </Container>
            </Fragment>
        );
    }

}


export default ModVoters;
