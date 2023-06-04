import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { Table, Button, notification, Spin } from "antd";
import Search from "../../../components/search";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../utils/axios";
// import axios from "axios";
import {
  PlusOutlined,
  ReloadOutlined,
  RightSquareOutlined,
  EditOutlined,
} from "@ant-design/icons";
import { useHistory } from "react-router-dom";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
// import { SEED_API } from "../../../GlobalVar";
import ShowDevice from "../../seed/ShowSeedDevice";
import Modal from "./modal";
import Swal from "sweetalert2";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../components/input/main.styles";
import { StyledButton } from "../../../components/button/main.styles";

let columnFilters = {};
let neData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [loading, setLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(neData);
  let [showDev, setShowDev] = useState(false);
  let [deviceData, setDeviceData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [inputValue, setInputValue] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const inputRef = useRef(null);
  const history = useHistory();
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };
  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };
  const showEditModal = () => {
    setIsModalVisible(true);
  };

  const opensweetalertdanger = () => {
    Swal.fire({
      title: "NO Device Data Found!",
      // text: "OOPS",
      type: "warning",
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const neRes = await axios.get(baseUrl + "/getAllItIps");
        neData = neRes.data;
        setDataSource(neData);
        setRowCount(neData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const showDeviceData = async (device_ip, device_type) => {
    await axios
      .post(baseUrl + "/showEDNInventoryData", {
        ip: device_ip,
        type: device_type,
      })
      .then((res) => {
        if ("msg" in res.data) {
          opensweetalertdanger();
          // alert("NO Device Data Found");
        } else {
          setDeviceData(res.data);
          setShowDev(true);
          console.log("device data===>", res.data);
        }
      })
      .catch((er) => {
        console.log("error", er);
      });
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(neData);
    setSortedInfo(null);
  };

  const handleInput = (e) => {
    let filteredSuggestions = neData.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
  };

  const convertToJson = (headers, fileData) => {
    let rows = [];
    fileData.forEach((row) => {
      const rowData = {};
      row.forEach((element, index) => {
        rowData[headers[index]] = element;
      });
      rows.push(rowData);
    });
    rows = rows.filter((value) => JSON.stringify(value) !== "{}");
    return rows;
  };

  const postData = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addITSeed", seed)
      .then((response) => {
        console.log("Ne post response===>", response);
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getAllItIps")
            .then((response) => {
              console.log("Ne response===>", response);
              neData = response.data;
              setDataSource(neData);
              setLoading(false);
            })
            .catch((error) => {
              console.log(error);
              setLoading(false);
            })
        );
        setLoading(false);
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  };

  const importFile = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    let data = null;
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
      const bstr = e.target.result;
      const workbook = XLSX.read(bstr, { type: "binary" });
      const workSheetName = workbook.SheetNames[0];
      const workSheet = workbook.Sheets[workSheetName];
      const fileData = XLSX.utils.sheet_to_json(workSheet, { header: 1 });
      const headers = fileData[0];
      const heads = headers.map((head) => ({ title: head, field: head }));
      fileData.splice(0, 1);
      data = convertToJson(headers, fileData);
      postData(data);
    };
  };

  useEffect(() => {
    inputRef.current.addEventListener("input", importFile);
  }, []);

  sortedInfo = sortedInfo || {};

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    {
      title: "IT IP-Address",
      dataIndex: "ip_address",
      key: "ip_address",
      // ...getColumnSearchProps("ip_address"),
      ...getColumnSearchProps(
        "ip_address",
        "IT IP-Address",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.ip_address.localeCompare(b.ip_address),
      // sortOrder: sortedInfo.columnKey === "ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Server Name",
      dataIndex: "server_name",
      key: "server_name",
      // ...getColumnSearchProps("server_name"),
      ...getColumnSearchProps(
        "server_name",
        "Server Name",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.server_name.localeCompare(b.server_name),
      // sortOrder: sortedInfo.columnKey === "server_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Application Name",
      dataIndex: "application_name",
      key: "application_name",
      // ...getColumnSearchProps("application_name"),
      ...getColumnSearchProps(
        "application_name",
        "Application Name",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.application_name.localeCompare(b.application_name),
      // sortOrder:
      //   sortedInfo.columnKey === "application_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Email",
      dataIndex: "owner_email",
      key: "owner_email",
      // ...getColumnSearchProps("owner_email"),
      ...getColumnSearchProps(
        "owner_email",
        "Owner Email",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.owner_email.localeCompare(b.owner_email),
      // sortOrder: sortedInfo.columnKey === "owner_email" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Owner Contact",
      dataIndex: "owner_contact",
      key: "owner_contact",
      // ...getColumnSearchProps("owner_contact"),
      ...getColumnSearchProps(
        "owner_contact",
        "Owner Contact",
        setRowCount,
        setDataSource,
        neData,
        columnFilters
      ),
      // sorter: (a, b) => a.owner_contact.localeCompare(b.owner_contact),
      // sortOrder: sortedInfo.columnKey === "owner_contact" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "",
    //   key: "edit",
    //   width: "10%",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{ width: "90%" }}
    //       onClick={() => {
    //         edit(record);
    //       }}
    //     >
    //       Edit
    //     </StyledButton>
    //   ),
    // },
    // {
    //   title: "",
    //   key: "edit",
    //   width: "10%",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{ width: "90%" }}
    //       onClick={() => {
    //         showDeviceData(record.ip_address, "It");
    //       }}
    //     >
    //       show
    //     </StyledButton>
    //   ),
    // },
  ];

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/dismantleOnBoardedDevice", {
          ips: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllOnBoardDevices")
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                neData = response.data;
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
          console.log(err);
          setLoading(false);
        });
    } else {
      opensweetalertdanger("No device is selected to delete.");
    }
  };

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        {showDev ? (
          <ShowDevice
            showSeed={showDev}
            setShowSeed={setShowDev}
            seedRecord={deviceData}
          />
        ) : null}

        {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            editRecord={editRecord}
          />
        )}

        <StyledHeading>
          EDN It List
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
          </span>
        </StyledHeading>
        {/* --------------------------------------------------- */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchValue} handleSeedInput={handleInput} />
          <StyledButton style={{}} onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; ADD DEVICE
          </StyledButton>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
            <RightSquareOutlined /> &nbsp; Delete
          </StyledButton>
          <div>
            <StyledImportFileInput
              type="file"
              value={inputValue}
              onChange={() => importFile}
              ref={inputRef}
            />
          </div>
        </div>
        {/* --------------------------------------------------- */}
        <Table
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="switch_ip_address"
        />
      </Spin>
    </>
  );
};

export default Index;

const StyledNeInput = styled.input`
  position: relative;
  cursor: pointer;
  height: 88%;
  border-radius: 5px;
  outline: 0;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;

  &:hover:after {
    background-color: #059140;
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  }
  &:after {
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
    background-color: #059142;
    font-weight: bolder;
    font-family: Montserrat-Regular;
    color: #fff;
    padding-top: 2%;
    font-size: 14px;
    text-align: center;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    content: "Upload EDN_IT_IPs";
    border-radius: 5px;
  }
`;
