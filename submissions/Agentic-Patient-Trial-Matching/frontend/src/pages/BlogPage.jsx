// frontend/src/pages/BlogPage.jsx
import React from 'react';
import { Typography, Box, Paper, Grid, Card, CardContent, CardHeader, Avatar, Divider } from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article'; // Main page icon
import SearchIcon from '@mui/icons-material/Search';
import FavoriteIcon from '@mui/icons-material/Favorite';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import HistoryIcon from '@mui/icons-material/History';

const mockBlogPosts = [
  {
    id: 1,
    title: "Streamlining Your Clinical Trial Search with AI Clinical Trial Matching",
    author: "Dr. Eva Innovate",
    authorAvatar: "EI", // Initials for Avatar
    avatarBgColor: "primary.main",
    date: "May 30, 2025",
    icon: <SearchIcon color="primary" />,
    excerpt: "Finding the right clinical trial can be a daunting task. Our new 'Find Clinical Trials' feature leverages advanced algorithms to match patient profiles with relevant ongoing studies. Simply enter a Patient ID, and let AI Clinical Trial Matching do the heavy lifting, presenting potential matches with detailed rationale.",
    content: `
      <p>The journey to finding a suitable clinical trial is often complex and time-consuming. Patients and healthcare providers navigate vast databases, trying to align specific medical conditions, stages, and biomarkers with trial eligibility criteria. AI Clinical Trial Matching aims to simplify this.</p>
      <p>Our core "Find Clinical Trials" functionality (accessible right from your dashboard!) uses a sophisticated backend system. When a Patient ID is entered:</p>
      <ul>
        <li>The system fetches the detailed patient profile.</li>
        <li>It then queries a comprehensive, up-to-date database of clinical trials.</li>
        <li>An intelligent matching algorithm analyzes inclusion/exclusion criteria, patient biomarkers, age, condition, and other relevant factors against each trial.</li>
        <li>Potential matches are presented clearly, along with a rationale for why the trial might be a good fit, and any potential flags or points to discuss with a healthcare professional.</li>
      </ul>
      <p>We believe this targeted approach not only saves valuable time but also empowers patients and their doctors to make more informed decisions about participating in clinical research.</p>
    `
  },
  {
    id: 2,
    title: "Never Lose Track: Introducing 'Favorites' and 'Saved Searches'",
    author: "Alex Organizer",
    authorAvatar: "AO",
    avatarBgColor: "secondary.main",
    date: "May 28, 2025",
    icon: <Box sx={{display: 'flex'}}><FavoriteIcon color="error" sx={{mr: 0.5}} /> <BookmarkIcon color="success" /></Box>,
    excerpt: "With so much information, it's easy to lose track of interesting trials or frequent search parameters. AI Clinical Trial Matching now offers 'Favorite Trials' and 'Saved Searches' to keep your research organized and accessible, all within your current session.",
    content: `
      <p>As you explore clinical trial options, you'll likely come across several trials that warrant further investigation or discussion. To help you manage this, we've integrated two key organizational features into AI Clinical Trial Matching:</p>
      <p><strong>Favorite Trials:</strong> Found a trial that looks promising? Simply click the heart icon on the trial card. This adds it to your 'Favorite Trials' list, accessible from the sidebar. You can review your favorites at any time during your session, making it easy to revisit and compare your top choices. Your list of favorites and the count in your 'Overview' panel are updated instantly.</p>
      <p><strong>Saved Searches:</strong> If you frequently search for trials using specific Patient IDs, our 'Save Search' button is for you! Located conveniently below the search input on your dashboard, this feature allows you to save the current Patient ID. Access your 'Saved Searches' from the sidebar to quickly re-run a search for that patient without retyping the ID. The 'Overview' panel also reflects how many searches you've saved.</p>
      <p>Both 'Favorites' and 'Saved Searches' are currently session-based, meaning they are remembered as long as your browser tab is open. We're exploring options for persistent storage in future updates!</p>
    `
  },
  {
    id: 3,
    title: "Dashboard Insights: Your Clinical Trial Journey at a Glance",
    author: "Chris Analyst",
    authorAvatar: "CA",
    avatarBgColor: "info.main",
    date: "May 25, 2025",
    icon: <HistoryIcon color="action" />,
    excerpt: "Our new dashboard provides a clear overview of your activity, including 'Trials Applied', 'Favorite Trials', and 'Saved Searches'. Plus, easily revisit the results of your last two searches directly on the dashboard.",
    content: `
      <p>The AI Clinical Trial Matching dashboard is designed to be your central hub for managing your clinical trial search. We've recently enhanced it to provide even more immediate insights:</p>
      <ul>
        <li><strong>Overview Panel:</strong> Quickly see key metrics like the number of searches you've performed ('Trials Applied' in our demo), how many trials you've favorited, and the count of your saved search terms. These numbers update in real-time as you interact with the platform.</li>
        <li><strong>Recent Search Results:</strong> No need to dig through notes or memory for that search you just ran. The dashboard now prominently displays the full card results for your last two unique Patient ID searches. This allows for quick review and comparison of recent findings. You can also conveniently re-run any of these historical searches with a single click.</li>
      </ul>
      <p>These features are designed to make your workflow more efficient, providing the information you need, when you need it, to support your clinical trial navigation.</p>
    `
  }
];


function BlogPage() {
  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <ArticleIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        AI Clinical Trial Matching Blog
      </Typography>
      <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
        Updates, insights, and news about the AI Clinical Trial Matching platform and clinical trial navigation.
      </Typography>
      <Grid container spacing={4}>
        {mockBlogPosts.map((post) => (
          <Grid item xs={12} key={post.id}> {/* Grid item with sizing (full width here) */}
            <Card variant="outlined">
              <CardHeader
                avatar={
                  <Avatar sx={{ bgcolor: post.avatarBgColor }} aria-label="author">
                    {post.authorAvatar}
                  </Avatar>
                }
                action={post.icon}
                titleTypographyProps={{variant:'h5', component:'h2', fontWeight:'medium'}}
                title={post.title}
                subheader={`${post.author} - ${post.date}`}
              />
              <CardContent>
                <Typography variant="body1" color="text.secondary" paragraph>
                  {post.excerpt}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box dangerouslySetInnerHTML={{ __html: post.content }} sx={{
                  '& p': { marginBottom: '1em', lineHeight: '1.6' },
                  '& ul': { paddingLeft: '20px', marginBottom: '1em' },
                  '& li': { marginBottom: '0.5em' },
                  '& strong': { fontWeight: 'bold' }
                }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
export default BlogPage;