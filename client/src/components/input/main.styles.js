import styled from "styled-components";

export const StyledImportFileInput = styled.input`
  position: relative;
  cursor: pointer;
  height: 86%;
  border-radius: 3px;
  outline: 0;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;

  &:hover:after {
    height: 25px;
    background-color: #059140;
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  }
  &:after {
    height: 25px;
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
    background-color: #059142;
    font-weight: bolder;
    font-family: Montserrat-Regular;
    color: #fff;
    padding-top: 1.2%;
    font-size: 11px;
    text-align: center;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    content: "Import From Excel";
    border-radius: 5px;
  }
`;
