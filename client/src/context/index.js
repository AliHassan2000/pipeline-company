import React, { useState, createContext } from "react";
import axios, { baseUrl } from "../utils/axios";

export const Context = createContext();

const Index = (props) => {
  const [excelData, setExcelData] = useState([]);
  const [onBoardedDevices, setOnBoardedDevices] = useState([]);
  const [seedDevices, setSeedDevices] = useState([]);
  const [sntc, setSNTC] = useState([]);
  const [pnCodeStats, setPnCodeStats] = useState([]);

  //inventory
  const [domain, setDomain] = useState("All");
  const [sites, setSites] = useState([]);
  const [racks, setRacks] = useState([]);
  const [devices, setDevices] = useState([]);
  const [boards, setBoards] = useState([]);
  const [subBoards, setSubBoards] = useState([]);
  const [sfps, setSFPs] = useState([]);
  const [licenses, setLicenses] = useState([]);

  //inventory
  const getSites = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);

    await axios
      .get(`${baseUrl}/getAllPhy${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setSites(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getRacks = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllRacks${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setRacks(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getDevices = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllDevices${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setDevices(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getBoards = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllBoards${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setBoards(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getSubBoards = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllSubboards${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setSubBoards(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getSFPs = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllSfps${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setSFPs(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getLicenses = async (domain = "All") => {
    let data = null;
    domain = domain === null ? "All" : domain;
    setDomain(domain);
    await axios
      .get(`${baseUrl}/getAllLicenses${domain === "All" ? "" : domain}`)
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setLicenses(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getPnCodeStats = async () => {
    let data = null;
    await axios
      .get(baseUrl + "/getPNCodeStatsPerCiscoDomain")
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setPnCodeStats(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getOnBoardedDevices = async (ipList = []) => {
    let data = null;
    if (ipList.length > 0) {
      await axios
        .post(baseUrl + "/onBoardDevice", ipList)
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllOnBoardDevices")
              .then((response) => {
                setOnBoardedDevices(response.data);
                data = response.data;
                setExcelData(response.data);
              })
              .catch((error) => {
                console.log(error);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
        });
    } else {
      try {
        const response = await axios.get(baseUrl + "/getAllOnBoardDevices");
        setOnBoardedDevices(response.data);
        data = response.data;
        setExcelData(response.data);
      } catch (err) {
        console.log(err);
      }
    }
    return data;
  };

  const getSeedDevices = async () => {
    let data = null;
    await axios
      .get(baseUrl + "/getSeeds")
      .then((response) => {
        console.log(response.data);
        data = response.data;
        setSeedDevices(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getSNTC = async () => {
    let data = null;
    await axios
      .get(baseUrl + "/getSNTC")
      .then((response) => {
        // console.log("wow papi ");
        console.log(response.data);
        data = response.data;
        setSNTC(response.data);
        setExcelData(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
    return data;
  };

  const getContext = () => {
    return {
      excelData,
      setExcelData,
      seedDevices,
      getSeedDevices,
      sntc,
      getSNTC,
      getOnBoardedDevices,
      onBoardedDevices,
      setOnBoardedDevices,
      sites,
      getSites,
      racks,
      getRacks,
      devices,
      getDevices,
      boards,
      getBoards,
      subBoards,
      getSubBoards,
      sfps,
      getSFPs,
      licenses,
      getLicenses,
      pnCodeStats,
      getPnCodeStats,
      domain,
      setDomain,
    };
  };

  return (
    <Context.Provider value={getContext()}>{props.children}</Context.Provider>
  );
};

export default Index;
