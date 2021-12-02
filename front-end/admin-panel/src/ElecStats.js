import './App.css';
import { Fragment, Component, createRef } from 'react';
import { Container, Row, Col} from 'react-bootstrap'
import axios from 'axios'

class ElecStats extends Component {

    constructor(props) {
        super(props);
        this.state = {
            allCandidates: [],
            voted: null,
            totalVoters: null
        };
        this.postSelectRef = createRef(null);
    }

    componentDidMount() {
        this.fetchStats();
    }

    fetchStats() {
        axios.get("/admin/election-statistics", { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                if (resp.data.allCandidates)
                    this.updateState("allCandidates", resp.data.allCandidates)
                if (resp.data.voters) {
                    this.updateState("voted", resp.data.voters.voted)
                    this.updateState("totalVoters", resp.data.voters.total)
                }
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


    render() {
        let data = this.state.allCandidates.map((candidates, index) => {
            let pos = candidates.position;
            let contestants = candidates.candidates.map((candidate, index) => {
                return (
                    <tr>
                        <td>{candidate.rollNo}</td>
                        <td>{candidate.name}</td>
                        <td>{candidate.votes}</td>
                    </tr>
                );
            });
            return (
                <div>
                    <div style={{fontWeight: "bold", fontSize:"large"}}>{pos}</div>
                    <table className="table table-condensed">
                        <thead>
                            <tr>
                                <th>Roll No.</th>
                                <th>Name</th>
                                <th>Votes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {contestants}
                        </tbody>
                    </table>
                </div>
            );
        });
        let totalVoters = this.state.totalVoters;
        let voted = this.state.voted;
        let voterTurnout = null;
        if (totalVoters!==null && totalVoters !==0 && voted!==null)
            voterTurnout = ((voted / totalVoters) * 100).toFixed(2) + '%';
        return (
            <Fragment>
                <Container className="access-cntl-tab">
                    <div className="d-grid gap-2">
                        <Row className="g-2">
                            <Col>
                                <div>Total Voters: {totalVoters}</div>
                            </Col>
                            <Col>
                                <div>Voted: {voted}</div>
                            </Col>
                            <Col>
                                <div>Voter Turnout: {voterTurnout}</div>
                            </Col>
                        </Row>

                    </div>
                    <Container>
                        {data}
                    </Container>
                </Container>
            </Fragment>
        );
    }

}


export default ElecStats;
