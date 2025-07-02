
interface SocialLinks {
  linkedin?: string;
  twitter?: string;
  github?: string;
}

export interface TeamMember {
  id: number;
  name: string;
  role: string;
  image: string;
  socialLinks: SocialLinks;
}

export const teamMembers: TeamMember[] = [
  {
    id: 1,
    name: "Yash K. Saini",
    role: "Lead Developer",
    image: "https://avatars.githubusercontent.com/u/115717039?v=4",
    socialLinks: {
      linkedin: "https://linkedin.com/in/yash_k_saini",
      twitter: "https://twitter.com/yashksaini",
      github: "https://github.com/yashksaini-coder"
    }
  }
];
