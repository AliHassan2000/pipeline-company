import React, { useState, useRef, useEffect } from "react";
import axios, { baseUrl } from "../../../../utils/axios";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import { Checkbox, Spin } from "antd";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
  DeleteOutlined,
  DeleteFilled,
} from "@ant-design/icons";
import Modal from "./modal";
import Swal from "sweetalert2";
import { roles } from "../../../../utils/constants.js";
import { getDataFromLocalStorage } from "../../../../utils/encrypt";

const Index = (props) => {
  const [user, setUser] = useState();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);

  useEffect(() => {
    const serviceCalls = async () => {
      setUser(getDataFromLocalStorage("user_encrypted"));
      try {
        setLoading(true);
        const res = await axios.post(
          baseUrl + "/getSecurityCoverageSummaryStatus",
          { domain: "EDN" }
        );
        setData(res.data);
        // setData(dummyData);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  // const dummyData = {
  //   "PAM Integrations": {
  //     "WFPB Console": ["6/6(C)", 100],
  //     "WFPB Nodes": ["6/6", 100],
  //   },
  //   "AAA Integrations": {
  //     "WFPB Console": ["10/100", 10],
  //     "WFPB Nodes": ["10/100", 10],
  //   },
  //   "BAA Integrations": {
  //     "WFPB Console": ["0/11", 0],
  //     "WFPB Nodes": ["8/0", "NaN"],
  //   },
  // };

  const generateTable = (data) => {
    let length = Object.keys(data).length;

    let table = Object.keys(data).map((yAxisHeader) => {
      let yAxisHeaderData = data[yAxisHeader];
      let cols = [];
      let col = Object.keys(yAxisHeaderData).map((xAxisHeader) => (
        <div
          style={{
            display: "flex",
            padding: "5px 5px 0 5px",
          }}
        >
          <div
            style={{
              border: "0px solid black",
              width: "70%",
              backgroundColor: "#009bdb",
              textAlign: "center",
              color: "white",
              marginRight: "5px",
              padding: "3px",
              borderRadius: "5px",
              //   fontWeight: "bold",
              minHeight: "28px",
            }}
          >
            {yAxisHeaderData[xAxisHeader][0]}
          </div>
          <div
            style={{
              border: "0px solid black",
              width: "30%",
              backgroundColor: "white",
              textAlign: "center",
              color: "#009bdb",
              padding: "3px",
              borderRadius: "5px",
              //   fontWeight: "bold",
            }}
          >
            {yAxisHeaderData[xAxisHeader][1]}
            {yAxisHeaderData[xAxisHeader][1] > 0 ? "%" : ""}
          </div>
        </div>
      ));

      col.unshift(
        <div style={{ display: "flex" }}>
          <div
            style={{
              margin: "0 5px 0 5px",
              border: "0px solid black",
              width: "70%",
              backgroundColor: "#009bdb",
              textAlign: "center",
              color: "white",
              padding: "3px",
              borderRadius: "5px",
              fontWeight: "bold",
            }}
          >
            Progress/Scope
          </div>
          <div
            style={{
              width: "30%",
              backgroundColor: "white",
              textAlign: "center",
              color: "#009bdb",
              margin: "0 5px 0 0",
              padding: "3px",
              borderRadius: "5px",
              fontWeight: "bold",
            }}
          >
            %
          </div>
        </div>
      );

      col.unshift(
        <div
          style={{
            backgroundColor: "grey",
            color: "white",
            borderRadius: "5px",
            textAlign: "center",
            margin: "5px",
            fontWeight: "bolder",
            padding: "3px",
          }}
        >
          {yAxisHeader}
        </div>
      );

      cols.push(
        <div
          style={{ border: "0px solid green", width: `${100 / (length + 1)}%` }}
        >
          {col}
        </div>
      );
      return cols;
    });

    let xAxisHeaders = Object.keys(Object.values(data)[0]).map(
      (xAxisHeader) => (
        <>
          <div
            style={{
              backgroundColor: "grey",
              textAlign: "center",
              color: "white",
              margin: "5px",
              padding: "3px",
              borderRadius: "5px",
              fontWeight: "bold",
            }}
          >
            {xAxisHeader !== "Total" && user?.user_role === roles.admin ? (
              <span
                style={{
                  backgroundColor: "white",
                  float: "left",
                  borderRadius: "3px",
                }}
              >
                <a style={{ color: "#bb0a1e", padding: "0 5px" }}>
                  <DeleteOutlined
                    onClick={() => {
                      deleteNode(xAxisHeader);
                    }}
                  />
                </a>
              </span>
            ) : null}
            {xAxisHeader}
            {xAxisHeader !== "Total" && user?.user_role === roles.admin ? (
              <span
                style={{
                  backgroundColor: "white",
                  float: "right",
                  borderRadius: "3px",
                }}
              >
                <a style={{ color: "#009bdb", padding: "0 5px" }}>
                  <EditOutlined
                    onClick={() => {
                      edit(xAxisHeader);
                    }}
                  />
                </a>
              </span>
            ) : null}
          </div>
        </>
      )
    );
    xAxisHeaders.unshift(
      <div
        style={{
          backgroundColor: "#009bdb",
          textAlign: "center",
          color: "white",
          margin: "5px",
          padding: "3px",
          borderRadius: "5px",
          fontWeight: "bold",
        }}
      >
        Nodes
      </div>
    );
    xAxisHeaders.unshift(
      <>
        {user?.user_role === roles.admin ? (
          <a>
            <div
              style={{
                backgroundColor: "#059142",
                textAlign: "center",
                color: "white",
                margin: "2px 5px 0 5px",
                padding: "3px",
                borderRadius: "5px",
                fontWeight: "bold",
              }}
              onClick={showModal}
            >
              <PlusOutlined /> &nbsp; Add Node
            </div>
          </a>
        ) : (
          <div
            style={{
              border: "0px solid black",
              margin: "5px",
              paddingBottom: "3px",
            }}
          >
            &nbsp;
          </div>
        )}
      </>
    );

    table.unshift(
      <div
        style={{
          border: "0px solid green",
          padding: "3px",
          width: `${100 / (length + 1)}%`,
        }}
      >
        {xAxisHeaders}
      </div>
    );

    return table;
  };

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const handleDelete = (node) => {
    axios
      .post(baseUrl + "/deleteNode", {
        node_name: node,
        domain: "EDN",
      })
      .then((res) => {
        console.log(res);
        Swal.fire("Deleted!", "Your item has been deleted.", "success");
        const promises = [];
        promises.push(
          axios
            .post(baseUrl + "/getSecurityCoverageSummaryStatus", {
              domain: "EDN",
            })
            .then((response) => {
              console.log(response.data);
              setData(response.data);
              setLoading(false);
            })
            .catch((error) => {
              console.log(error);
              setLoading(false);
            })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        Swal.fire("Error!", "Your item has not been deleted.", "failure");
        console.log(err);
        setLoading(false);
      });
  };

  const deleteNode = (node) => {
    Swal.fire({
      title: "Are you sure?",
      text: `You will not be able to recover this node "${node}"!`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "No, cancel!",
      reverseButtons: true,
    }).then((result) => {
      if (result.dismiss === Swal.DismissReason.cancel) {
        // User clicked the cancel button
        // Swal.fire("Cancelled", "Your item is safe :)", "error");
      } else {
        handleDelete(node);
      }
    });
  };

  const edit = async (node) => {
    const res = await axios.post(baseUrl + "/getNodeDataByNodeName", {
      node_name: node,
      domain: "EDN",
    });
    // setEditRecord({
    //   node_id: 1,
    //   node_name: "ACI",
    //   functions: ["a", "b", "c"],
    //   pn_codes: ["w", "x", "y", "z"],
    // });
    setEditRecord(res.data);
    setIsModalVisible(true);
  };

  return (
    <>
      {isModalVisible && (
        <Modal
          isModalVisible={isModalVisible}
          setIsModalVisible={setIsModalVisible}
          setData={setData}
          editRecord={editRecord}
        />
      )}

      <Spin tip="Loading..." spinning={loading}>
        <StyledHeading>EDN Dashboard</StyledHeading>
        {data ? (
          <div
            style={{
              display: "flex",
              border: "0px solid red",
              backgroundColor: "#e6e6e6",
              padding: "5px",
              borderRadius: "10px",
            }}
          >
            {generateTable(data)}
          </div>
        ) : (
          <StyledHeading style={{ color: "red", fontSize: "14px" }}>
            No data to show
          </StyledHeading>
        )}
      </Spin>
    </>
  );
};

export default Index;
