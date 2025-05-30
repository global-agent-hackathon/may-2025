// https://arxiv.org/

import Exa from 'exa-js';
import dotenv from 'dotenv';
import express from 'express';
import nodemailer from 'nodemailer';
import bodyParser from 'body-parser';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import cron from 'node-cron';
import { initDatabase, addSubscriber, getSubscribers, updateLastSent, removeSubscriber } from './db.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const exa = new Exa(process.env.EXA_API_KEY);

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.set('view engine', 'ejs');
app.set('views', join(__dirname, 'views'));

// Add flash message middleware
app.use((req, res, next) => {
  res.locals.message = req.query.message;
  res.locals.messageType = req.query.messageType;
  next();
});

// Initialize database
await initDatabase();

// Cache for papers
let paperCache = {
    papers: [],
    lastUpdated: null,
    CACHE_DURATION: 24 * 60 * 60 * 1000 // 24 hours in milliseconds
};

// Configure nodemailer
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

// Function to send welcome email
const sendWelcomeEmail = async (email) => {
    try {
        await transporter.sendMail({
            from: process.env.EMAIL_USER,
            to: email,
            subject: "Welcome to the Research Papers Newsletter!",
            html: `
                <h1>Welcome to the Research Papers Newsletter!</h1>
                <p>Thank you for subscribing to our daily research papers newsletter. You'll receive the latest research papers from arXiv.org every day at 12:40 PM IST.</p>
                <p>What to expect:</p>
                <ul>
                    <li>Daily summaries of the latest research papers</li>
                    <li>Direct links to the full papers</li>
                    <li>Key findings and implications</li>
                </ul>
                <p>If you wish to unsubscribe at any time, you can click the unsubscribe link at the bottom of any newsletter email.</p>
                <p>Best regards,<br>The Research Papers Team</p>
            `
        });
        console.log(`Welcome email sent to ${email}`);
    } catch (error) {
        console.error(`Error sending welcome email to ${email}:`, error);
        throw error;
    }
};

// Helper function to add delay between API calls
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Function to check if cache is valid
const isCacheValid = () => {
    if (!paperCache.lastUpdated) return false;
    const now = new Date().getTime();
    return (now - paperCache.lastUpdated) < paperCache.CACHE_DURATION;
};

// Function to fetch latest arXiv papers and generate summary
const fetchAndSummarizePapers = async (forceRefresh = false) => {
    try {
        // Return cached papers if they're still valid and not forcing refresh
        if (!forceRefresh && isCacheValid()) {
            console.log('Returning cached papers');
            return paperCache.papers;
        }

        console.log('Fetching new papers...');
        // Search for latest papers from arXiv
        const searchResults = await exa.search("site:arxiv.org", {
            numResults: 3,
            sortBy: "publishedDate",
            sortOrder: "desc",
            includeDomains: ["arxiv.org"],
        });

        // Get contents of the papers
        const paperContents = await exa.getContents(
            searchResults.results.map(result => result.url),
            { text: true }
        );

        // Generate summary for each paper with rate limiting
        const summaries = [];
        for (const paper of paperContents.results) {
            try {
                await delay(1000);
                
                const summary = await exa.answer(
                    `Summarize this research paper in a blog post format suitable for a newsletter. Include key findings and implications: ${paper.text}`,
                    {
                        text: true,
                        model: "exa-pro",
                    }
                );
                
                summaries.push({
                    title: paper.title,
                    url: paper.url,
                    summary: summary.answer,
                    fetchedAt: new Date().toISOString()
                });
                
                console.log(`Successfully processed paper: ${paper.title}`);
            } catch (error) {
                console.error(`Error processing paper ${paper.title}:`, error.message);
                continue;
            }
        }

        // Update cache
        paperCache.papers = summaries;
        paperCache.lastUpdated = new Date().getTime();

        return summaries;
    } catch (error) {
        console.error("Error in fetchAndSummarizePapers:", error.message);
        return paperCache.papers; // Return cached papers if available, even if expired
    }
};

// Function to send newsletter to all subscribers
const sendNewsletterToSubscribers = async () => {
    try {
        console.log('\n=== Starting Newsletter Delivery Process ===');
        console.log('Time:', new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
        
        // Check if there are any subscribers
        const subscribers = await getSubscribers();
        console.log(`Found ${subscribers.length} subscribers`);
        
        if (subscribers.length === 0) {
            console.log('No subscribers found, skipping newsletter delivery');
            return;
        }

        console.log('\nFetching latest papers...');
        const papers = await fetchAndSummarizePapers(true); // Force refresh for daily newsletter
        if (!papers || papers.length === 0) {
            console.log("No papers available to send");
            return;
        }
        console.log(`Successfully fetched ${papers.length} papers`);

        // Create email content
        const emailContent = papers.map((paper, index) => `
            <h2>${index + 1}. ${paper.title}</h2>
            <p><a href="${paper.url}">Read Paper</a></p>
            <div>${paper.summary}</div>
            <hr>
        `).join('');

        // Send email to all subscribers
        console.log('\nStarting to send emails to subscribers...');
        for (const subscriber of subscribers) {
            try {
                console.log(`\nAttempting to send newsletter to ${subscriber.email}...`);
                await transporter.sendMail({
                    from: process.env.EMAIL_USER,
                    to: subscriber.email,
                    subject: "Daily Research Papers Newsletter",
                    html: `
                        <h1>Daily Research Papers Newsletter</h1>
                        <p>Last updated: ${new Date(paperCache.lastUpdated).toLocaleString()}</p>
                        ${emailContent}
                        <p>To unsubscribe, please click <a href="${process.env.BASE_URL}/unsubscribe?email=${subscriber.email}">here</a>.</p>
                    `
                });
                await updateLastSent(subscriber.email);
                console.log(`✅ Successfully sent newsletter to ${subscriber.email}`);
            } catch (error) {
                console.error(`❌ Error sending newsletter to ${subscriber.email}:`, error);
                // Continue with next subscriber even if one fails
            }
        }
        console.log('\n=== Newsletter Delivery Process Completed ===\n');
    } catch (error) {
        console.error("\n❌ Error in sendNewsletterToSubscribers:", error);
    }
};

// Schedule daily newsletter at 12:40 PM IST (07:10 AM UTC)
console.log('\nSetting up cron job for 12:40 PM IST (07:10 AM UTC)...');
cron.schedule('10 7 * * *', async () => {
    console.log('\n=== Cron Job Triggered ===');
    console.log('Time:', new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    try {
        await sendNewsletterToSubscribers();
    } catch (error) {
        console.error('❌ Error in cron job:', error);
    }
}, {
    scheduled: true,
    timezone: "Asia/Kolkata" // Set timezone to IST
});

// Add a test endpoint to manually trigger the newsletter
app.get('/test-newsletter', async (req, res) => {
    try {
        console.log('Manual newsletter trigger requested');
        await sendNewsletterToSubscribers();
        res.send('Newsletter delivery process completed. Check server logs for details.');
    } catch (error) {
        console.error('Error in manual newsletter trigger:', error);
        res.status(500).send('Error sending newsletter. Check server logs for details.');
    }
});

// Routes
app.get('/', async (req, res) => {
    try {
        const forceRefresh = req.query.refresh === 'true';
        const papers = await fetchAndSummarizePapers(forceRefresh);
        const subscribers = await getSubscribers();
        res.render('newsletter', { 
            papers: papers || [],
            subscribers: subscribers,
            lastUpdated: paperCache.lastUpdated ? new Date(paperCache.lastUpdated).toLocaleString() : 'Never'
        });
    } catch (error) {
        console.error("Error rendering newsletter:", error);
        res.status(500).send("Error loading newsletter");
    }
});

app.post('/subscribe', async (req, res) => {
    try {
        const { email } = req.body;
        if (email) {
            const subscriber = await addSubscriber(email);
            if (subscriber) {
                // Send welcome email only if the subscription was successful
                await sendWelcomeEmail(email);
                res.redirect('/');
            } else {
                res.status(400).send("Already subscribed");
            }
        } else {
            res.status(400).send("Email is required");
        }
    } catch (error) {
        console.error("Error subscribing:", error);
        res.status(500).send("Error subscribing to newsletter");
    }
});

// Update unsubscribe route to handle both GET and POST
app.get('/unsubscribe', async (req, res) => {
  try {
    const { email } = req.query;
    if (email) {
      await removeSubscriber(email);
      res.redirect('/?message=Successfully unsubscribed from the newsletter&messageType=success');
    } else {
      res.redirect('/?message=Email is required&messageType=error');
    }
  } catch (error) {
    console.error("Error unsubscribing:", error);
    res.redirect('/?message=Error unsubscribing from newsletter&messageType=error');
  }
});

app.post('/unsubscribe', async (req, res) => {
  try {
    const { email } = req.body;
    if (!email) {
      return res.redirect('/?message=Email is required&messageType=error');
    }

    const subscribers = await getSubscribers();
    const isSubscribed = subscribers.some(sub => sub.email === email);

    if (!isSubscribed) {
      return res.redirect('/?message=This email is not subscribed to the newsletter&messageType=error');
    }

    await removeSubscriber(email);
    res.redirect('/?message=Successfully unsubscribed from the newsletter&messageType=success');
  } catch (error) {
    console.error("Error unsubscribing:", error);
    res.redirect('/?message=Error unsubscribing from newsletter&messageType=error');
  }
});

app.post('/send-newsletter', async (req, res) => {
    try {
        await sendNewsletterToSubscribers();
        res.redirect('/');
    } catch (error) {
        console.error("Error sending newsletter:", error);
        res.status(500).send("Error sending newsletter");
    }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});