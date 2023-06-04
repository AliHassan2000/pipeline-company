import React, { useState, useEffect, useContext } from "react";
import styled from "styled-components";
import {
  Table,
  Button,
  Spin,
  notification,
  Modal,
  Input,
  Menu,
  Dropdown,
} from "antd";
import Search from "../../../components/search";
import { StyledButton } from "../../../components/button/main.styles";
import axios, { baseUrl } from "../../../utils/axios";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import ShowDeviceModal from "./showOnBoardedDevice";
import {
  PlusOutlined,
  RightSquareOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { Context } from "../../../context";
// import { SEED_API } from "../../GlobalVar";
import Swal from "sweetalert2";
import XLSX from "xlsx";
import { roles } from "../../../utils/constants";

let columnFilters = {};
// let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const history = useHistory();
  const location = useLocation();
  const [user, setUser] = useState();
  const {
    excelData,
    setExcelData,
    getOnBoardedDevices,
    onBoardedDevices,
    setOnBoardedDevices,
  } = useContext(Context);
  let [devicesToOnBoard, setDevicesToOnBoard] = useState([]);
  let [exportLoading, setExportLoading] = useState(false);
  let [dismantleLoading, setDismantleLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [fDataSource, setFDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isFModalVisible, setIsFModalVisible] = useState(false);
  const [deviceData, setDeviceData] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  let selectedDevices = [];
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [loadingText, setLoadingText] = useState("Loading ...");
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  //---------------------------------------
  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      if (typeof location.state !== "undefined") {
        const ipList = location.state.detail.map((item) => item.ne_ip_address);
        history.replace({
          pathname: "/onboard",
          state: { detail: [] },
        });
        // console.log(ipList);
        // let data = await getOnBoardedDevices(ipList);
        // console.log(data);
        // setRowCount(data.length);
        // setDataSource(data);

        await axios
          .post(baseUrl + "/onBoardDevice", ipList)
          .then((response) => {
            if (response?.response?.status == 500) {
              openSweetAlert(response?.response?.data?.response, "error");
            } else {
              openSweetAlert(`All Devices Onboarded Successfully`, "success");
            }
            const promises = [];
            promises.push(
              axios
                .get(baseUrl + "/getAllOnBoardDevices")
                .then((response) => {
                  console.log(response.data);
                  setDataSource(response.data);
                  setExcelData(response.data);
                  setOnBoardedDevices(response.data);
                  // excelData = response.data;
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
        setLoading(false);
      } else {
        try {
          if (onBoardedDevices.length === 0) {
            let data = await getOnBoardedDevices();
            console.log(data);
            // setExcelData(data);
            setRowCount(data.length);
            setDataSource(data);
          } else {
            setRowCount(onBoardedDevices.length);
            setDataSource(onBoardedDevices);
            setExcelData(onBoardedDevices);
          }
          setLoading(false);

          // const res = await axios.get(baseUrl + "/getAllOnBoardDevices");
          // setDataSource(res.data);
          // excelData = res.data;
          // setRowCount(excelData.length);
          setLoading(false);
        } catch (err) {
          console.log(err);
          setLoading(false);
        }
      }
    };
    serviceCalls();
  }, []);

  const getFailedDevice = async () => {
    let date = new Date();
    let month = date.getMonth() + 1;
    let dateString = `${date.getDate()}-${
      month < 10 ? "0" + month : month
    }-${date.getFullYear()}`;
    console.log(date.getFullYear());
    try {
      await axios
        .post(baseUrl + "/getFailedDevices", { date: dateString })
        .then((res) => {
          setFDataSource(res.data);
          console.log(res);
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const openNotification = () => {
    notification.open({
      message: "Inventory File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const jsonToExcel = (data) => {
    let wb = XLSX.utils.book_new();
    let binaryData = XLSX.utils.json_to_sheet(data);
    XLSX.utils.book_append_sheet(wb, binaryData, "onboardeddevices");
    XLSX.writeFile(wb, "onboardeddevices.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    // setLoadingText("Exporting ...");
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
    // setLoading(true);
    // await axios
    //   .get(baseUrl + "/exportInventory")
    //   .then((response) => {
    //     // openNotification();
    //     jsonToExcel(response.data);
    //     console.log(response);
    //     // setLoading(false);
    //     // setLoadingText("Loading ...");
    //   })
    //   .catch((error) => {
    //     setExportLoading(false);
    //     console.log(error);
    //   });
  };

  const handleDisMantle = () => {
    if (selectedRowKeys.length > 0) {
      Swal.fire({
        title: "Are you sure, you want to dismantle selected devices?",
        type: "warning",
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: `Confirm`,
        cancelButtonText: `Cancel`,
      }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.value) {
          // alert(selectedRowKeys.length);
          setDismantleLoading(true);
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
                    excelData = response.data;
                    setLoading(false);
                    setRowCount(response.data.length);
                    setSelectedRowKeys([]);
                    setDismantleLoading(false);
                  })
                  .catch((error) => {
                    console.log(error);
                    setLoading(false);
                    setDismantleLoading(false);
                  })
              );
              return Promise.all(promises);
            })
            .catch((err) => {
              console.log(err);
              setLoading(false);
              setDismantleLoading(false);
            });
        } else {
          // alert("bye");
        }
      });
    } else {
      opensweetalertdanger("No device is selected to dismantle.");
    }
  };

  const handleOffload = () => {
    if (selectedRowKeys.length > 0) {
      Swal.fire({
        title: "Are you sure, you want to Offload selected devices?",
        type: "warning",
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: `Confirm`,
        cancelButtonText: `Cancel`,
      }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.value) {
          // alert(selectedRowKeys.length);
          setDismantleLoading(true);
          axios
            .post(baseUrl + "/offloadOnBoardedDevice", {
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
                    excelData = response.data;
                    setLoading(false);
                    setRowCount(response.data.length);
                    setSelectedRowKeys([]);
                    setDismantleLoading(false);
                  })
                  .catch((error) => {
                    console.log(error);
                    setLoading(false);
                    setDismantleLoading(false);
                  })
              );
              return Promise.all(promises);
            })
            .catch((err) => {
              console.log(err);
              setLoading(false);
              setDismantleLoading(false);
            });
        } else {
          // alert("bye");
        }
      });
    } else {
      opensweetalertdanger("No device is selected to offload.");
    }
  };

  const handlePoweroff = () => {
    if (selectedRowKeys.length > 0) {
      Swal.fire({
        title: "Are you sure, you want to power off selected devices?",
        type: "warning",
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: `Confirm`,
        cancelButtonText: `Cancel`,
      }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.value) {
          // alert(selectedRowKeys.length);
          setDismantleLoading(true);
          axios
            .post(baseUrl + "/powerOffOnBoardedDevice", {
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
                    excelData = response.data;
                    setLoading(false);
                    setRowCount(response.data.length);
                    setSelectedRowKeys([]);
                    setDismantleLoading(false);
                  })
                  .catch((error) => {
                    console.log(error);
                    setLoading(false);
                    setDismantleLoading(false);
                  })
              );
              return Promise.all(promises);
            })
            .catch((err) => {
              console.log(err);
              setLoading(false);
              setDismantleLoading(false);
            });
        } else {
          // alert("bye");
        }
      });
    } else {
      opensweetalertdanger("No device is selected to power off.");
    }
  };

  const opensweetalertdanger = (title) => {
    Swal.fire({
      title,
      type: "warning",
    });
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const remove = (item) => {
    console.log(selectedDevices);
    console.log(item);
    var index = selectedDevices.indexOf(item);
    if (index !== -1) {
      selectedDevices.splice(index, 1);
    }
  };

  const showDevice = async (device_ip) => {
    await axios
      .post(baseUrl + "/getOnBoardDevice", {
        ip: device_ip,
      })
      .then((res) => {
        setDeviceData(res.data);
        console.log("device data===>", res.data);
        setIsModalVisible(true);
      })
      .catch((er) => {
        console.log("error", er);
      });
  };

  const handleSeedInput = (e) => {
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

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const columns = [
    {
      title: "Ip Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "ne_ip_address",
        "Ip Address",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      render: (text, record) => (
        <a
          onClick={() => {
            showDevice(record.ne_ip_address);
          }}
        >
          {text}
        </a>
      ),
      // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
      // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // width: "4%",
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Name",
      dataIndex: "device_name",
      key: "device_name",
      // width: "250px",
      // ...getColumnSearchProps("device_name"),
      ...getColumnSearchProps(
        "device_name",
        "Device Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_name.length - b.device_name.length,
      // sortOrder: sortedInfo.columnKey === "device_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("rack_id"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rack_id - b.rack_id,
      // sortOrder: sortedInfo.columnKey === "rack_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id - b.site_id,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacture Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      // ...getColumnSearchProps("manufactuer_date"),
      ...getColumnSearchProps(
        "manufactuer_date",
        "Manufacture Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "HW EOS Date",
      dataIndex: "hw_eos_date",
      key: "hw_eos_date",
      // ...getColumnSearchProps("hw_eos_date"),
      ...getColumnSearchProps(
        "hw_eos_date",
        "HW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eos_date.length - b.hw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "HW EOL Date",
      dataIndex: "hw_eol_date",
      key: "hw_eol_date",
      // ...getColumnSearchProps("hw_eol_date"),
      ...getColumnSearchProps(
        "hw_eol_date",
        "HW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eol_date.length - b.hw_eol_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOS Date",
      dataIndex: "sw_eos_date",
      key: "sw_eos_date",
      // ...getColumnSearchProps("sw_eos_date"),
      ...getColumnSearchProps(
        "sw_eos_date",
        "SW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eos_date.length - b.sw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOL Date",
      dataIndex: "sw_eol_date",
      key: "sw_eol_date",
      // ...getColumnSearchProps("sw_eol_date"),
      ...getColumnSearchProps(
        "sw_eol_date",
        "SW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eol_date.length - b.sw_eol_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Virtual",
      dataIndex: "virtual",
      key: "virtual",
      // ...getColumnSearchProps("virtual"),
      ...getColumnSearchProps(
        "virtual",
        "Virtual",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.virtual.length - b.virtual.length,
      // sortOrder: sortedInfo.columnKey === "virtual" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "authentication",
        "Authentication",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Subrack Id Number",
      dataIndex: "subrack_id_number",
      key: "subrack_id_number",
      // ...getColumnSearchProps("subrack_id_number"),
      ...getColumnSearchProps(
        "subrack_id_number",
        "Subrack Id Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.subrack_id_number.length - b.subrack_id_number.length,
      // sortOrder:
      //   sortedInfo.columnKey === "subrack_id_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Criticality",
      dataIndex: "criticality",
      key: "criticality",
      // ...getColumnSearchProps("criticality"),
      ...getColumnSearchProps(
        "criticality",
        "Criticality",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.criticality.length - b.criticality.length,
      // sortOrder: sortedInfo.columnKey === "criticality" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Function",
      dataIndex: "function",
      key: "function",
      // ...getColumnSearchProps("function"),
      ...getColumnSearchProps(
        "function",
        "Function",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.function.length - b.function.length,
      // sortOrder: sortedInfo.columnKey === "function" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Cisco Domain",
      dataIndex: "cisco_domain",
      key: "cisco_domain",
      // ...getColumnSearchProps("domain"),
      ...getColumnSearchProps(
        "cisco_domain",
        "Cisco Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.domain.length - b.domain.length,
      // sortOrder: sortedInfo.columnKey === "domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Patch Version",
      dataIndex: "patch_version",
      key: "patch_version",
      // ...getColumnSearchProps("patch_version"),
      ...getColumnSearchProps(
        "patch_version",
        "Patch Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.patch_version.length - b.patch_version.length,
      // sortOrder: sortedInfo.columnKey === "patch_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Section",
      dataIndex: "section",
      key: "section",
      // ...getColumnSearchProps("section"),
      ...getColumnSearchProps(
        "section",
        "Section",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.section.length - b.section.length,
      // sortOrder: sortedInfo.columnKey === "section" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Software Version",
      dataIndex: "software_version",
      key: "software_version",
      // ...getColumnSearchProps("software_version"),
      ...getColumnSearchProps(
        "software_version",
        "Software Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.software_version.length - b.software_version.length,
      // sortOrder:
      //   sortedInfo.columnKey === "software_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Hardware Version",
      dataIndex: "hardware_version",
      key: "hardware_version",
      // ...getColumnSearchProps("hardware_version"),
      ...getColumnSearchProps(
        "hardware_version",
        "Hardware Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hardware_version.length - b.hardware_version.length,
      // sortOrder:
      //   sortedInfo.columnKey === "hardware_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "department",
        "Department",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("serial_number"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.serial_number.length - b.serial_number.length,
      // sortOrder: sortedInfo.columnKey === "serial_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "RFS Date",
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "dismantle_date",
      key: "dismantle_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "dismantle_date",
        "Dismantle Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Pn Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("pn_code"),
      ...getColumnSearchProps(
        "pn_code",
        "Pn Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.pn_code.length - b.pn_code.length,
      // sortOrder: sortedInfo.columnKey === "pn_code" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Tag Id",
      dataIndex: "tag_id",
      key: "tag_id",
      // ...getColumnSearchProps("tag_id"),
      ...getColumnSearchProps(
        "tag_id",
        "Tag Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.tag_id.length - b.tag_id.length,
      // sortOrder: sortedInfo.columnKey === "tag_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Max Power",
      dataIndex: "max_power",
      key: "max_power",
      // ...getColumnSearchProps("max_power"),
      ...getColumnSearchProps(
        "max_power",
        "Max Power",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.max_power.length - b.max_power.length,
      // sortOrder: sortedInfo.columnKey === "max_power" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Ru",
      dataIndex: "device_ru",
      key: "device_ru",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "device_ru",
        "Device Ru",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "domain",
      key: "domain",
      // ...getColumnSearchProps("domain"),
      ...getColumnSearchProps(
        "domain",
        "Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.domain.length - b.domain.length,
      // sortOrder: sortedInfo.columnKey === "domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_code",
      key: "item_code",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_code",
        "Item Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_desc",
      key: "item_desc",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_desc",
        "Item Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "clei",
      key: "clei",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "clei",
        "Clei",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacturer",
      dataIndex: "manufacturer",
      key: "manufacturer",
      // ...getColumnSearchProps("manufacturer"),
      ...getColumnSearchProps(
        "manufacturer",
        "Manufacturer",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufacturer.length - b.manufacturer.length,
      // sortOrder: sortedInfo.columnKey === "manufacturer" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Stack",
      dataIndex: "stack",
      key: "stack",
      // ...getColumnSearchProps("stack"),
      ...getColumnSearchProps(
        "stack",
        "Stack",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.stack.length - b.stack.length,
      // sortOrder: sortedInfo.columnKey === "stack" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Parent",
      dataIndex: "parent",
      key: "parent",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "parent",
        "Parent",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "VULN Fix Plan Status",
      dataIndex: "vuln_fix_plan_status",
      key: "vuln_fix_plan_status",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_fix_plan_status",
        "VULN Fix Plan Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "vuln_ops_severity",
      key: "vuln_ops_severity",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_ops_severity",
        "VULN OPS Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Source",
      dataIndex: "source",
      key: "source",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "source",
        "Source",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Type",
      dataIndex: "site_type",
      key: "site_type",
      // ...getColumnSearchProps("site_type"),
      ...getColumnSearchProps(
        "site_type",
        "Site Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_type.length - b.site_type.length,
      // sortOrder: sortedInfo.columnKey === "site_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Contract Number",
      dataIndex: "contract_number",
      key: "contract_number",
      // ...getColumnSearchProps("contract_number"),
      ...getColumnSearchProps(
        "contract_number",
        "Contract Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.contract_number.length - b.contract_number.length,
      // sortOrder: sortedInfo.columnKey === "contract_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Contract Expiry",
      dataIndex: "contract_expiry",
      key: "contract_expiry",
      // ...getColumnSearchProps("contract_expiry"),
      ...getColumnSearchProps(
        "contract_expiry",
        "Contract Expiry",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.contract_expiry.length - b.contract_expiry.length,
      // sortOrder: sortedInfo.columnKey === "contract_expiry" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "IMS Status",
      dataIndex: "ims_status",
      key: "ims_status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "ims_status",
        "IMS Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },

    {
      title: "IMS Function",
      dataIndex: "ims_function",
      key: "ims_function",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "ims_function",
        "IMS Function",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    ////////////////////////////////////////////
    {
      dataIndex: "integrated_with_aaa",
      key: "integrated_with_aaa",
      ...getColumnSearchProps(
        "integrated_with_aaa",
        "Integrated with AAA",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_paam",
      key: "integrated_with_paam",
      ...getColumnSearchProps(
        "integrated_with_paam",
        "Integrated with PAAM",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "approved_mbss",
      key: "approved_mbss",
      ...getColumnSearchProps(
        "approved_mbss",
        "Approved MBSS",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_implemented",
      key: "mbss_implemented",
      ...getColumnSearchProps(
        "mbss_implemented",
        "MBSS Implemented",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_integration_check",
      key: "mbss_integration_check",
      ...getColumnSearchProps(
        "mbss_integration_check",
        "MBSS Integration Check",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_siem",
      key: "integrated_with_siem",
      ...getColumnSearchProps(
        "integrated_with_siem",
        "Integrated with Siem",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "threat_cases",
      key: "threat_cases",
      ...getColumnSearchProps(
        "threat_cases",
        "Threat Cases",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_scanning",
      key: "vulnerability_scanning",
      ...getColumnSearchProps(
        "vulnerability_scanning",
        "Vulnerability Scanning",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_severity",
      key: "vulnerability_severity",
      ...getColumnSearchProps(
        "vulnerability_severity",
        "Vulnerability Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    ////////////////////////////////////////////
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "",
    //   key: "show",
    //   width: "1.6%",
    //   fixed: "right",
    //   render: (text, record) => (
    //     <StyledButton
    //       color={"#009BDB"}
    //       style={{
    //         width: "90%",
    //         fontSize: "10px",
    //         height: "25px",
    //         margin: "0px",
    //       }}
    //       onClick={() => {
    //         showDevice(record.ne_ip_address);
    //       }}
    //     >
    //       Show
    //     </StyledButton>
    //   ),
    // },
  ];

  const handleClose = () => {
    // setDataSource(null);
    setIsFModalVisible(false);
  };

  const fColumns = [
    {
      title: "Ip Address",
      dataIndex: "ip_address",
      key: "ip_address",
      ...getColumnSearchProps("ip_address"),
      sorter: (a, b) => a.ip_address - b.ip_address,
      sortOrder: sortedInfo.columnKey === "ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Date",
      dataIndex: "date",
      key: "date",
      ...getColumnSearchProps("date"),
      sorter: (a, b) => a.date - b.date,
      sortOrder: sortedInfo.columnKey === "date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Time",
      dataIndex: "time",
      key: "time",
      ...getColumnSearchProps("time"),
      sorter: (a, b) => a.time - b.time,
      sortOrder: sortedInfo.columnKey === "time" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Reason",
      dataIndex: "reason",
      key: "reason",
      ...getColumnSearchProps("reason"),
      sorter: (a, b) => a.reason - b.reason,
      sortOrder: sortedInfo.columnKey === "reason" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  // let excelTemplate = [
  //   {
  //     ne_ip_address: "",
  //     device_id: "",
  //     device_name: "",
  //     rack_id: "",
  //     site_id: "",
  //     manufactuer_date: "",
  //     hw_eos_date: "",
  //     hw_eol_date: "",
  //     sw_eos_date: "",
  //     sw_eol_date: "",
  //     virtual: "",
  //     authentication: "",
  //     subrack_id_number: "",
  //     criticality: "",
  //     function: "",
  //     domain: "",
  //     patch_version: "",
  //     section: "",
  //     software_version: "",
  //     hardware_version: "",
  //     department: "",
  //     serial_number: "",
  //     rfs_date: "",
  //     pn_code: "",
  //     tag_id: "",
  //     max_power: "",
  //     device_ru: "",
  //     manufacturer: "",
  //     status: "",
  //     creation_date: "",
  //     modification_date: "",
  //   },
  // ];
  // const jsonToExcelTemplate = (seedData) => {
  //   let wb = XLSX.utils.book_new();
  //   let binarySeedData = XLSX.utils.json_to_sheet(seedData);
  //   XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
  //   XLSX.writeFile(wb, "SNTC.xlsx");
  // };
  // const exportTemplate = async () => {
  //   jsonToExcelTemplate(excelTemplate);
  //   openNotification();
  // };

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
    setExportLoading(false);
  };

  const menu = (
    <Menu style={{ marginTop: "-220px", height: "90px" }}>
      <Menu.Item
        key="0"
        style={{ backgroundColor: "transparent", padding: "0px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportSeed}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export All
        </StyledButton>
      </Menu.Item>
      <Menu.Item
        key="1"
        style={{ backgroundColor: "transparent", padding: "5px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportFiltered}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export Filtered
        </StyledButton>
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Spin tip={loadingText} spinning={loading}>
        {isModalVisible ? (
          <ShowDeviceModal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            deviceData={deviceData}
          />
        ) : null}

        <Modal
          style={{ zIndex: "99999" }}
          width="80%"
          title=""
          closable={false}
          visible={isFModalVisible}
          footer=""
        >
          <div
            style={{
              textAlign: "center",
              fontSize: "15px",
              fontWeight: "bolder",
            }}
          >
            Failed Onboarded Devices
          </div>
          <br />
          {fDataSource ? (
            <StyledTable
              pagination={{
                defaultPageSize: 50,
                pageSizeOptions: [50, 100, 500, 1000],
              }}
              scroll={{ x: 1000 }}
              // pagination={{
              //   defaultPageSize: 50,
              //   defaultPageSize: 8,
              // }}
              columns={fColumns}
              dataSource={fDataSource}
              rowKey="ne_ip_address"
            />
          ) : (
            <div
              style={{
                textAlign: "center",
                height: "100%",
                paddingBottom: "30px",
              }}
            >
              <Spin tip="Loading Data ..." spinning={true} />
            </div>
          )}
          <div
            style={{
              display: "flex",
              justifyContent: "right",
              paddingTop: "20px",
            }}
          >
            <StyledButton color={"red"} onClick={handleClose}>
              Close
            </StyledButton>
          </div>
        </Modal>

        <StyledHeading>
          On Boarded Devices Detail
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
          </span>
        </StyledHeading>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
        </div>
        <div
          style={{
            padding: "0 0 0px 0",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          {/* <Link to="/onboard"> */}
          <div
            style={{
              display: "flex",
            }}
          >
            <Spin spinning={dismantleLoading}>
              <StyledButton
                onClick={handleDisMantle}
                color={"#009BDB"}
                disabled={user?.user_role === roles.user}
              >
                <PlusOutlined /> &nbsp; Dismantle
              </StyledButton>
            </Spin>
            &nbsp;
            <Spin spinning={dismantleLoading}>
              <StyledButton
                onClick={handleOffload}
                color={"#009BDB"}
                disabled={user?.user_role === roles.user}
              >
                <PlusOutlined /> &nbsp; Offload
              </StyledButton>
            </Spin>
            &nbsp;
            <Spin spinning={dismantleLoading}>
              <StyledButton
                onClick={handlePoweroff}
                color={"#009BDB"}
                disabled={user?.user_role === roles.user}
              >
                <PlusOutlined /> &nbsp; Power Off
              </StyledButton>
            </Spin>
          </div>

          <div style={{ display: "flex" }}>
            <StyledButton
              color={"#bb0a1e"}
              onClick={() => {
                getFailedDevice();
                setIsFModalVisible(true);
              }}
              disabled={user?.user_role === roles.user}
            >
              <RightSquareOutlined /> &nbsp; Show Failed devices
            </StyledButton>
            &nbsp;
            {/* <StyledButton color={"#3bbdc2"} onClick={exportTemplate}>
              <RightSquareOutlined /> &nbsp; Export Template
            </StyledButton>
            &nbsp;&nbsp;&nbsp; */}
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
          </div>
        </div>
        {/* <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
        </div> */}

        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          scroll={{ x: 13000, y: height - 350 }}
          rowSelection={user?.user_role !== roles.user ? rowSelection : null}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
          rowKey="ne_ip_address"
          // pagination={{
          //   defaultPageSize: 50,
          //   defaultPageSize: 10,
          // }}
        />
      </Spin>
    </>
  );
};

export default Index;
