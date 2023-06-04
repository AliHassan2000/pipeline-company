import "./App.css";
import React, { useState, useEffect } from "react";
import { ThemeProvider } from "styled-components";
import theme from "./theme";
import Landing from "./containers/landing";
// import TestLanding from "./containers/testLanding";
import LogIn from "./containers/login";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Context from "./context";
import { getDataFromLocalStorage } from "./utils/encrypt";

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    // const token = localStorage.getItem("cisco_mobily_token");
    const tokenFromLocalStorage = getDataFromLocalStorage(
      "cisco_mobily_token_encrypted"
    );
    setToken(tokenFromLocalStorage);
    console.log(tokenFromLocalStorage);
  }, []);

  return (
    <Context>
      <ThemeProvider theme={theme}>
        <Router>
          <Switch>
            {token ? (
              <>
                <Route exact path="/*" component={Landing} />
                {/* <Route exact path="/" component={Landing} />
                <Route exact path="/landing" component={Landing} />
                <Route exact path="/seed" component={Landing} />
                <Route exact path="/onboard" component={Landing} />
                <Route exact path="/sites" component={Landing} />
                <Route exact path="/racks" component={Landing} />
                <Route exact path="/rebd" component={Landing} />
                <Route exact path="/iostracker" component={Landing} />
                <Route exact path="/pos" component={Landing} />
                <Route exact path="/functions" component={Landing} />
                <Route exact path="/domains" component={Landing} />
                <Route exact path="/devices" component={Landing} />
                <Route exact path="/boards" component={Landing} />
                <Route exact path="/subboards" component={Landing} />
                <Route exact path="/sfps" component={Landing} />
                <Route exact path="/licenses" component={Landing} />
                <Route exact path="/operations" component={Landing} />
                <Route exact path="/edn" component={Landing} />
                <Route exact path="/nelist" component={Landing} />
                <Route exact path="/seclist" component={Landing} />
                <Route exact path="/itlist" component={Landing} />
                <Route exact path="/sntc" component={Landing} />
                <Route exact path="/staticonboarding" component={Landing} />
                <Route exact path="/edntompls" component={Landing} />
                <Route exact path="/ednipt" component={Landing} />
                <Route exact path="/igwsystems" component={Landing} />
                <Route exact path="/ednsystems" component={Landing} />
                <Route exact path="/security" component={Landing} />
                <Route exact path="/edncdplegacy" component={Landing} />
                <Route exact path="/ednmaclegacy" component={Landing} />
                <Route exact path="/ednmaclegacysearch" component={Landing} />
                <Route exact path="/edndashboard" component={Landing} />
                <Route exact path="/ednlldpaci" component={Landing} />
                <Route exact path="/ednarp" component={Landing} />
                <Route exact path="/igwaci" component={Landing} />
                <Route exact path="/igwcdplegacy" component={Landing} />
                <Route exact path="/ednlldplegacy" component={Landing} />
                <Route exact path="/igwlldplegacy" component={Landing} />
                <Route exact path="/igwmaclegacy" component={Landing} />
                <Route exact path="/ednmaster" component={Landing} />
                <Route exact path="/igwmaster" component={Landing} />
                <Route exact path="/pncodestats" component={Landing} />
                <Route exact path="/iptdashboard" component={Landing} />
                <Route exact path="/iptendpoints" component={Landing} />
                <Route exact path="/accesspoints" component={Landing} />
                <Route exact path="/addmember" component={Landing} />
                <Route exact path="/ednnetdashboard" component={Landing} />
                <Route exact path="/igwnetdashboard" component={Landing} />
                <Route exact path="/ednsysdashboard" component={Landing} />
                <Route exact path="/igwsysdashboard" component={Landing} />
                <Route exact path="/socdashboard" component={Landing} />
                <Route exact path="/ednipam" component={Landing} />
                <Route exact path="/ednipamdashboard" component={Landing} />
                <Route exact path="/igwipam" component={Landing} />
                <Route exact path="/igwipamdashboard" component={Landing} />
                <Route exact path="/dccapacityedn" component={Landing} />
                <Route exact path="/dccapacityigw" component={Landing} />
                <Route
                  exact
                  path="/dccapacityedndashboard"
                  component={Landing}
                />
                <Route
                  exact
                  path="/dccapacityigwdashboard"
                  component={Landing}
                />
                <Route exact path="/cdn" component={Landing} />
                <Route exact path="/ednservices" component={Landing} />
                <Route exact path="/igwservices" component={Landing} />
                <Route exact path="/igwlinks" component={Landing} />
                <Route exact path="/powerfeeds" component={Landing} />
                <Route exact path="/ednexchange" component={Landing} />
                <Route exact path="/edncorerouting" component={Landing} />
                <Route exact path="/vrfowners" component={Landing} />
                <Route exact path="/externalvrfanalysis" component={Landing} />
                <Route exact path="/intranetvrfanalysis" component={Landing} />
                <Route exact path="/received-routes" component={Landing} />
                <Route exact path="/ednexchangedashboard" component={Landing} />
                <Route
                  exact
                  path="/servicemappingdashboard"
                  component={Landing}
                />
                <Route exact path="/physicalservers" component={Landing} />
                <Route exact path="/app" component={Landing} />
                <Route exact path="/os" component={Landing} />
                <Route exact path="/mac" component={Landing} />
                <Route exact path="/ip" component={Landing} />
                <Route exact path="/owner" component={Landing} />

                <Route exact path="/iptassignmenttracker" component={Landing} />
                <Route exact path="/iptrmatracker" component={Landing} />
                <Route exact path="/iptclearancetracker" component={Landing} />
                <Route exact path="/ednpowerofftracker" component={Landing} />
                <Route exact path="/ednhandbacktracker" component={Landing} />
                <Route exact path="/ednhandovertracker" component={Landing} />
                <Route exact path="/pmrtracker" component={Landing} />
                <Route exact path="/snags" component={Landing} />
                <Route exact path="/backups" component={Landing} />

                <Route exact path="/updateidip" component={Landing} />
                <Route
                  exact
                  path="/bulkupdatemultiplecolumns"
                  component={Landing}
                />
                <Route
                  exact
                  path="/bulkupdatesinglecolumn"
                  component={Landing}
                />
                <Route exact path="/deletedeviceinseed" component={Landing} />
                <Route exact path="/ednipamfaileddevices" component={Landing} />
                <Route exact path="/igwipamfaileddevices" component={Landing} />
                <Route
                  exact
                  path="/accesspointsfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/edndccapacityfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwdccapacityfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednexchangefaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/inventoryfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/iptendpointsfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednphysicalmappingfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednphysicalmappingcdplegacyfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednphysicalmappinglldpfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednservicemappingfirewallarpfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednservicemappingmacfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwphysicalmappingfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwphysicalmappingcdplegacyfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwphysicalmappinglldpfaileddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwphysicalmappingmacfaileddevices"
                  component={Landing}
                />
                <Route exact path="/f5faileddevices" component={Landing} />
                <Route
                  exact
                  path="/securityoperationdashboard"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilitydashboard"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilitymaster"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilityarcher"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilitynotfounddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilitynoplandevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilityinprogress"
                  component={Landing}
                />
                <Route
                  exact
                  path="/ednvulnerabilitymanagedby"
                  component={Landing}
                />
                <Route exact path="/ednvulnerabilityopen" component={Landing} />
                <Route
                  exact
                  path="/ednvulnerabilityoverdue"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilitydashboard"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilitymaster"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilityarcher"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilitynotfounddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilitynoplandevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/socvulnerabilitydashboard"
                  component={Landing}
                />
                <Route
                  exact
                  path="/socvulnerabilitymaster"
                  component={Landing}
                />
                <Route
                  exact
                  path="/socvulnerabilityarcher"
                  component={Landing}
                />
                <Route
                  exact
                  path="/socvulnerabilitynotfounddevices"
                  component={Landing}
                />
                <Route
                  exact
                  path="/igwvulnerabilitynoplandevices"
                  component={Landing}
                />

                <Route exact path="/f5" component={Landing} />
                <Route exact path="/f5dashboard" component={Landing} /> */}
              </>
            ) : (
              <>
                <Route exact path="/" component={LogIn} />
              </>
            )}
          </Switch>
        </Router>
      </ThemeProvider>
    </Context>
  );
}

export default App;

// HTTPS=true
// SSL_CRT_FILE=.cert/cert.pem
// SSL_KEY_FILE=.cert/key.pem
