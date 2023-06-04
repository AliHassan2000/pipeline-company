import React from "react";
import styled from "styled-components";
import { FilterOutlined, SearchOutlined } from "@ant-design/icons";

const search = (props) => {
  return (
    <StyledSearch>
      <div>
        <SearchOutlined
          style={{ fontSize: "15px", paddingTop: "45%", color: "silver" }}
        />
      </div>
      <StyledInput value={props.searchValue} onChange={props.handleSeedInput} />
      <div>
        <FilterOutlined
          style={{ fontSize: "20px", paddingTop: "25%", color: "#009bdb" }}
        />
      </div>
    </StyledSearch>
  );
};

const StyledSearch = styled.div`
  box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px,
    rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;
  border: 2px solid white;
  border-radius: 20px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 0 15px 0 15px;
`;

const StyledInput = styled.input`
  border: none;
  outline: none;
  width: 95%;
  padding-left: 10px;
`;

export default search;
