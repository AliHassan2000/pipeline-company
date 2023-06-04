import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { Table, Button, notification, Spin, Modal, Tabs } from "antd";
import Search from "../../../../../components/search";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../../../utils/axios";
import {
  PlusOutlined,
  ReloadOutlined,
  RightSquareOutlined,
  EditOutlined,
  DownloadOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useHistory } from "react-router-dom";
import { columnSearch } from "../../../../../utils";
import useWindowDimensions from "../../../../../hooks/useWindowDimensions";
import { StyledHeading } from "../../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../../components/input/main.styles";
import { StyledButton } from "../../../../../components/button/main.styles";
import Swal from "sweetalert2";
import Attachment from "./attachment";
// import "Blob";

let columnFilters = {};
let excelData = [];
const Index = ({ record, setIsAttachmentModalVisible }) => {
  let [attachments, setAttachments] = useState([]);
  const { height, width } = useWindowDimensions();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(excelData);
  let [showDev, setShowDev] = useState(false);
  let [deviceData, setDeviceData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [searchSecValue, setSearchSecValue] = useState(null);
  let [searchNeValue, setSearchNeValue] = useState(null);
  let [inputNEValue, setInputNeValue] = useState("");
  let [inputSecValue, setInputSecValue] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const inputNe = useRef(null);
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
  const [file, setFile] = useState(null);
  const [reload, setReload] = useState(true);

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

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const res = await axios.get(
          baseUrl +
            `/getAttachmentsById?trackerId=${record.handover_tracker_id}&category=edn_ho_tracker`
        );
        excelData = res.data;
        setDataSource(res.data);
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(excelData);
    setSortedInfo(null);
  };

  const handleNeInput = (e) => {
    let filteredSuggestions = excelData.filter(
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

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  sortedInfo = sortedInfo || {};

  const handleDownload = async (record) => {
    await axios
      .get(
        baseUrl + `/downloadAttachment?attachment_id=${record.attachment_id}`,
        { responseType: "blob" }
      )
      .then((response) => {
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });

        // Create a URL for the file
        const url = URL.createObjectURL(blob);

        // Create an <a> tag to initiate the download
        const a = document.createElement("a");
        a.href = url;
        a.download = record.file_name + "." + record.file_extension;
        document.body.appendChild(a);
        a.click();

        // Clean up the URL after use
        URL.revokeObjectURL(url);
        console.log(response);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const handleView = async (record) => {
    await axios
      .get(baseUrl + `/viewAttachment?attachment_id=${record.attachment_id}`, {
        responseType: "blob",
      })
      .then((response) => {
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });
        const url = URL.createObjectURL(blob);
        window.open(url);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const columns = [
    {
      dataIndex: "file_name",
      key: "file_name",
      ...getColumnSearchProps(
        "file_name",
        "File Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "file_extension",
      key: "file_extension",
      ...getColumnSearchProps(
        "file_extension",
        "File Extension",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      key: "download",
      width: "60px",

      render: (text, record) => (
        <a style={{ paddingLeft: "25px" }}>
          <DownloadOutlined onClick={() => handleDownload(record)} />
        </a>
      ),
    },
    {
      key: "view",
      width: "90px",

      render: (text, record) => (
        <a style={{ paddingLeft: "25px" }}>
          <EyeOutlined onClick={() => handleView(record)} />
        </a>
      ),
    },
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
        .post(baseUrl + "/deleteAttachments", {
          ids: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(
                baseUrl +
                  `/getAttachmentsById?trackerId=${record.handover_tracker_id}&category=edn_ho_tracker`
              )
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                excelData = response.data;
                setRowCount(excelData.length);
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
      openSweetAlert("No item is selected to delete.", "danger");
    }
  };

  let seedTemp = [
    {
      ip_address: "", //Not Null
      device_id: "", //drop down (Completed/Pending)
      assigned_to: "", //drop down from endpoint "/getAssignees"
      region: "",
      project_type: "", //Not Null
      site_type: "",
      asset_type: "", //Not Null
      pid: "", //drop down (Yes/No)
      serial_number: "",
      handover_submisson_date: "",
      handover_completion_date: "", //Not Null
      handover_review_status: "",
      remedy_incident: "", //Not Null
    },
  ];

  const openNotification = () => {
    notification.open({
      message: "File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "snaglist");
    XLSX.writeFile(wb, "snaglist.xlsx");
    setExportLoading(false);
  };

  const exportTemplate = async () => {
    jsonToExcel(seedTemp);
    openNotification();
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const addAttachments = async (device) => {
    let url = "/ednHandoverTracker?category=edn_ho_tracker";
    try {
      await axios
        .post(baseUrl + url, device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
            setReload((prev) => !prev);
          }
          const promises = [];
          promises.push(
            axios
              .get(
                baseUrl +
                  `/getAttachmentsById?trackerId=${record.handover_tracker_id}&category=edn_ho_tracker`
              )
              .then((response) => {
                excelData = response.data;
                setDataSource(response.data);
                setRowCount(excelData.length);
                // setLoading(false);
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
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmit = () => {
    if (attachments.length == 0) {
      alert("No Attachments Selected");
    } else {
      console.log(record);
      let ho = {
        handover_tracker_id: record.handover_tracker_id,
        ip_address: record.ip_address,
        device_id: record.device_id,
        assigned_to: record.assigned_to,
        project_type: record.project_type,
        handover_submisson_date: record.handover_submisson_date,
        handover_completion_date: record.handover_completion_date,
        handover_review_status: record.handover_review_status,
        remedy_incident: record.remedy_incident,
        region: record.region,
        site_type: record.site_type,
        asset_type: record.asset_type,
        pid: record.pid,
        serial_number: record.serial_number,
        comment: record.comment,
        attachments,
      };

      if (record.primary_ho_id !== "") {
        ho["primary_ho_id"] = record.primary_ho_id;
      }

      // let ho = [
      //   {
      //     handover_tracker_id: trackerId,
      //     attachments,
      //   },
      // ];

      addAttachments([ho]);
    }
  };

  return (
    <Modal
      style={{ marginTop: "10px", zIndex: "99999" }}
      width="80%"
      title=""
      closable={false}
      visible={true}
      footer=""
    >
      <>
        <Spin tip="Loading..." spinning={loading}>
          <>
            <StyledHeading>
              Attachments
              <span
                style={{
                  float: "right",
                  fontSize: "14px",
                  fontWeight: "bold",
                  color: "grey",
                  paddingTop: "10px",
                }}
              >
                Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns:
                {columns.length - 2}
              </span>
            </StyledHeading>

            {/* <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0 0 10px 0",
                }}
              >
                <Search
                  searchValue={searchNeValue}
                  handleSeedInput={handleNeInput}
                />
                <StyledButton onClick={showModal} color={"#009BDB"}>
                  <PlusOutlined /> &nbsp; Add New Snag
                </StyledButton>
              </div> */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "0 0 10px 0",
              }}
            >
              <div>
                <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
                  <RightSquareOutlined /> &nbsp; Delete
                </StyledButton>
                &nbsp;
                {/* <input
                  type="file"
                  value={file}
                  onChange={() => importExcel}
                  //   ref={inputNe}
                /> */}
                {/* <Attachment
                  response={attachments}
                  setResponse={setAttachments}
                /> */}
              </div>

              <div style={{ display: "flex" }}>
                {/* <StyledButton onClick={showModal} color={"#009BDB"}>
                  <PlusOutlined /> &nbsp; Save Attachment
                </StyledButton> */}
                {/* &nbsp; */}
                {/* <Spin spinning={exportLoading}>
                  <StyledButton color={"#3bbdc2"} onClick={exportSeed}>
                    <RightSquareOutlined /> &nbsp; Export Snags
                  </StyledButton>
                </Spin> */}
                &nbsp;
                <StyledButton
                  onClick={() => setIsAttachmentModalVisible(false)}
                  color={"#bb0a1e"}
                >
                  <RightSquareOutlined /> &nbsp; Close
                </StyledButton>
              </div>
            </div>
            {/* --------------------------------------------------- */}
            <StyledTabs defaultActiveKey="1">
              <Tabs.TabPane tab="Attachments List" key="1">
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
                  rowKey="attachment_id"
                />
              </Tabs.TabPane>
              <Tabs.TabPane tab="Add Attachment" key="2">
                <div style={{ textAlign: "center" }}>
                  {reload ? (
                    <Attachment
                      response={attachments}
                      setResponse={setAttachments}
                    />
                  ) : (
                    <Attachment
                      response={attachments}
                      setResponse={setAttachments}
                    />
                  )}
                  <br />
                  <StyledButton color={"green"} onClick={handleSubmit}>
                    Add Attachments
                  </StyledButton>
                </div>
              </Tabs.TabPane>
            </StyledTabs>
            {/* <Table
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
              rowKey="attachment_id"
            /> */}
          </>
        </Spin>
      </>
    </Modal>
  );
};

export default Index;

const StyledTabs = styled(Tabs)`
  /* margin-top: -20px; */
  .ant-tabs-content-holder {
    border: none;
    border-left: none !important;
    padding: 3px;
  }
`;

// const StyledButton = styled(Button)`
//   width: 15%;
//   font-family: Montserrat-Regular;
//   box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
//   background-color: ${(props) => props.color};
//   border-color: ${(props) => props.color};
//   color: white;
//   border-radius: 5px;
//   &:focus,
//   &:hover {
//     background-color: ${(props) => props.color};
//     border-color: ${(props) => props.color};
//     color: white;
//     opacity: 0.8;
//   }
// `;
