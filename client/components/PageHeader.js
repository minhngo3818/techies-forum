import { Box, Container } from "@mui/material";

// styling
const headerStyle = {
  display: "flex",
  justifyContent: "center",
  margin: "2rem",
  color: "white",
};

const PageHeader = (props) => {
  const pageName = props.pageName;
  return (
    <Container>
      <Box sx={headerStyle}>
        <h3>{pageName}</h3>
      </Box>
    </Container>
  );
};

export default PageHeader;