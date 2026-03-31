import { Container, Typography, Button, Box } from "@mui/material";
import Link from "next/link";

export default function Home() {
  return (
    <Container maxWidth="md">
      <Box textAlign="center" mt={8}>
        <Typography variant="h3" gutterBottom>
          Welcome to Mock Interview Platform 🎤
        </Typography>
        <Typography variant="h5" color="grey">
          Practice technical interviews with AI-driven conversations
        </Typography>
        <Link href="/interview">
          <Button variant="contained" color="primary" sx={{ mt: 4 }}>
            Start Technical Interview
          </Button>
        </Link>
      </Box>
    </Container>
  );
}
